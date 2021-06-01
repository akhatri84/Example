from pathlib import Path
from os import path
from django.conf import settings
import random
import os
from decouple import config, Csv
import mimetypes

from django.utils import timezone
from django.db.models import Q

import graphene
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from urllib.parse import urlparse
import boto3
from botocore.exceptions import NoCredentialsError
from urllib.parse import urlparse

from .models import ProductFilesModel
from product.models import ProductModel

ACCESS_KEY = config('AWS_ACCESS_KEY')
SECRET_KEY = config('AWS_SECRET_KEY')
REGION_NAME = config('REGION_NAME')
BUCKET = config('BUCKET_NAME')

def get_bucket_file_folder(aws_file_url):
    o = urlparse(aws_file_url, allow_fragments=False)
    return o.path.lstrip('/')


def file_extention(path):
    return os.path.splitext(path)[1]


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()


    def resolve_total_count(self, info):
        return ProductFilesModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length



class ProductFilesType(DjangoObjectType):
    class Meta:
        model = ProductFilesModel
        filter_fields = {
            'file_type': ['exact', 'icontains', 'istartswith','contains'],
            'file_extension': ['exact', 'icontains', 'istartswith','contains'],
            'aws_file_url': ['exact', 'icontains', 'istartswith','contains'],
            'file_size': ['exact', 'icontains', 'istartswith','contains'],
            'productfile_name': ['exact', 'icontains', 'istartswith','contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    productfile = relay.Node.Field(ProductFilesType)  
    all_productfiles = DjangoFilterConnectionField(ProductFilesType, productfile_pk=graphene.Int(), product_id=graphene.Int(), search=graphene.String(),
                                                orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_productfiles(self, info, productfile_pk=None, product_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        productfile_search = ProductFilesModel.objects.all()

        if productfile_pk:
            productfile_search = productfile_search.filter(pk=productfile_pk)
        if product_id:
            productfile_search = productfile_search.filter(product_id=product_id)
        if orderBy:
            productfile_search = productfile_search.order_by(*orderBy)
        if search:
            productfile_search = productfile_search.filter(
                Q(file_type__icontains=search) |
                Q(file_extension__icontains=search) |
                Q(aws_file_url__icontains=search) |
                Q(file_size__icontains=search)|
                Q(productfile_name__icontains=search)
            )
        return productfile_search


class ProductFileInput(graphene.InputObjectType):
    productfiles_id = graphene.Int()
    product_file = graphene.String()


class UploadProductFile(graphene.Mutation):
    productfile = graphene.Field(ProductFilesType)

    class Arguments:
        product_file = Upload(required=True)
        s3_file = graphene.String()
        product_id = graphene.Int()
        file_type = graphene.String()

    success = graphene.Boolean()
    presignedUrl = graphene.String()

    def mutate(self, info, product_file, product_id, file_type, s3_file=None):

        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        #for product_file in info.context.FILES:
        file_extension = file_extention(str(product_file))
        file_format = mimetypes.types_map[file_extension]

        if file_extension.lower() not in [".jpg",".png",".jpeg" ,".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex", ".txt",".wpd"]:
            raise GraphQLError(send_err_res.raiseError("Valid File", "NP"))
        else:
            
            productfile = ProductFilesModel()

            try:
                product = ProductModel.objects.get(pk=product_id, deleted=0)
            except:
                product = None

            if product == None:
                return GraphQLError(send_err_res.raiseError("Product", "NV"))
            
            filename = timezone.now().strftime("%Y%m%d-%H%M%S")
            tempfile = settings.MEDIA_ROOT + default_storage.save(filename + file_extention(str(product_file)),ContentFile(product_file.read()))
            s3_file = f"{product_id}" + "_product/" + str(product_id) + "-" + filename + file_extension
            productfile.product_id = product
            productfile.file_type = file_type
            productfile.file_extension = file_extension
            productfile.aws_file_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_file}"
            productfile.file_size = str(round((path.getsize(tempfile) / 1000), 1)) + " KB"
            productfile.productfile_name = str(product_file)
            productfile.created_at = timezone.now()
            productfile.updated_at = timezone.now()
            productfile.updated_by = product.user_id.appusers_id
            productfile.deleted = 0
            
            try:
                if file_extension.lower() in [".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex", ".txt",".wpd"]:
                    s3.upload_file(tempfile, BUCKET, s3_file,ExtraArgs={ 'ACL': 'private','ContentType':file_format})
                else:
                    s3.upload_file(tempfile, BUCKET, s3_file,ExtraArgs={ 'ACL': 'public-read','ContentType':file_format})

                productfile.save()

                # create presigned_url
                presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET,'Key': get_bucket_file_folder(productfile.aws_file_url)},ExpiresIn=300)
            
                if os.path.isfile(tempfile):
                    os.remove(tempfile)
                
                return UploadProductFile(success=True,presignedUrl=presigned_url,productfile=productfile)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass                
        

class DownloadProductFile(graphene.Mutation):
    class Arguments:
        product_file = graphene.String()

    success = graphene.Boolean()
    presigned_url = graphene.String()

    def mutate(self, info, product_file):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)

        product_file = get_bucket_file_folder(product_file)

        try:
            s3.head_object(Bucket=BUCKET, Key=product_file)
            presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': product_file},
                                                      ExpiresIn=300)  
            return DownloadProductFile(success=True, presigned_url=str(presigned_url))          
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass     
        


class DeleteProductFile(graphene.Mutation):
    productfiles_id = graphene.Int()

    class Arguments:
        data = graphene.List(ProductFileInput, required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, data):
        s3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        i = 0
        for d in data:

            product_file = get_bucket_file_folder(d.product_file)
            delete_product_file = ProductFilesModel.objects.filter(productfiles_id=d.productfiles_id).first()

            delete_product_file.deleted = 1

            productfiles_id = d.productfiles_id
            try:
                s3.Object(BUCKET, product_file).delete()
                delete_product_file.save()
                i = i + 1
                if i == len(data):
                    return DeleteProductFile(productfiles_id)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass
              


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    upload_product_file = UploadProductFile.Field()
    download_product_file = DownloadProductFile.Field()
    delete_product_file = DeleteProductFile.Field()



