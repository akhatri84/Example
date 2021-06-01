import sys

sys.path.append('../')
from pathlib import Path
from os import path
import random
from django.utils import timezone
import io
import os.path
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import base64
from urllib.parse import urlparse
import mimetypes
from django.db.models import Q

import graphene
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res
from decouple import config, Csv
import boto3
from botocore.exceptions import NoCredentialsError

from .models import SupplychainFilesModel
from supplychain.models import SupplychainModel

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
        return SupplychainFilesModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class SupplychainFilesType(DjangoObjectType):
    class Meta:
        model = SupplychainFilesModel
        filter_fields = {
            'file_type': ['exact', 'icontains', 'istartswith','contains'],
            'file_extension': ['exact', 'icontains', 'istartswith','contains'],
            'aws_file_url': ['exact', 'icontains', 'istartswith','contains'],
            'file_size':['exact', 'icontains', 'istartswith','contains'],
            'supplychain_filename':['exact', 'icontains', 'istartswith','contains'],
            'deleted' : ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    supply_chain_file = relay.Node.Field(SupplychainFilesType)
    all_supplychainfiles = DjangoFilterConnectionField(SupplychainFilesType, supplychainfile_pk=graphene.Int(),
                                                       supply_chain_id=graphene.Int(), search=graphene.String(),
                                                       orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_supplychainfiles(self, info, supplychainfile_pk=None, supply_chain_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        supply_chain_file_search = SupplychainFilesModel.objects.all()

        if supplychainfile_pk:
            supply_chain_file_search = supply_chain_file_search.filter(pk=supplychainfile_pk)
        if supply_chain_id:
            supply_chain_file_search = supply_chain_file_search.filter(supply_chain_id=supply_chain_id)
        if orderBy:
            supply_chain_file_search = supply_chain_file_search.order_by(*orderBy)
        if search:
            supply_chain_file_search = supply_chain_file_search.filter(
                Q(file_type__icontains=search) |
                Q(file_extension__icontains=search) |
                Q(aws_file_url__icontains=search)|
                Q(file_size__icontains=search)|
                Q(supplychain_filename__icontains=search)
            )
        return supply_chain_file_search


class SupplychainFilesInput(graphene.InputObjectType):
    supplychainfiles_id = graphene.Int(required=True)
    supplychain_document = graphene.String()


class UploadSupplychainDocument(graphene.Mutation):
    supply_chain_document = graphene.Field(SupplychainFilesType)

    class Arguments:
        supplychain_document = Upload(required=True)
        s3_file = graphene.String()
        supply_chain_id = graphene.Int()

    success = graphene.Boolean()
    presignedUrl = graphene.String()

    def mutate(self, info, supplychain_document, supply_chain_id, s3_file=None):

        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        file_extension = file_extention(str(supplychain_document))
        file_format = mimetypes.types_map[file_extension]

        if file_extension.lower() not in [".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex", ".txt", ".wpd"]:
            raise GraphQLError(send_err_res.raiseError("Valid File", "NP"))
        else:
            supply_chain_document = SupplychainFilesModel()

            try:
                supplychain = SupplychainModel.objects.get(pk=supply_chain_id, deleted=0)
            except:
                supplychain = None

            if supplychain == None:
                return GraphQLError(send_err_res.raiseError("Supplychain", "NV"))

            filename = timezone.now().strftime("%Y%m%d-%H%M%S")

            tempfile = settings.MEDIA_ROOT + default_storage.save(filename + file_extention(str(supplychain_document)),
                                                                  ContentFile(supplychain_document.read()))

            s3_file = f"{supply_chain_id}" + "_supplychain/" + str(supply_chain_id) + "-" + filename + file_extension
            supply_chain_document.supply_chain_id = supplychain
            supply_chain_document.file_type = "doc"
            supply_chain_document.file_extension = file_extension
            supply_chain_document.aws_file_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_file}"
            supply_chain_document.file_size = str(round((path.getsize(tempfile) / 1000), 1)) + " KB"
            supply_chain_document.supplychain_filename = str(supplychain_document)
            supply_chain_document.created_at = timezone.now()
            supply_chain_document.updated_at = timezone.now()
            supply_chain_document.updated_by = supplychain.user_id.appusers_id
            supply_chain_document.deleted = 0

            try:
                supply_chain_document.save()
                s3.upload_file(tempfile, BUCKET, s3_file, ExtraArgs={'ACL': 'private', 'ContentType': file_format})

                # create presigned_url
                presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET,
                                                                                'Key': get_bucket_file_folder(
                                                                                    supply_chain_document.aws_file_url)},
                                                          ExpiresIn=300)

                if os.path.isfile(tempfile):
                    os.remove(tempfile)

                return UploadSupplychainDocument(success=True, presignedUrl=presigned_url,
                                                 supply_chain_document=supply_chain_document)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass


class DownloadSupplychainDocument(graphene.Mutation):
    class Arguments:
        supplychain_document = graphene.String()

    success = graphene.Boolean()
    presigned_url = graphene.String()

    def mutate(self, info, supplychain_document):

        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        supplychain_document = get_bucket_file_folder(supplychain_document)

        try:
            s3.head_object(Bucket=BUCKET, Key=supplychain_document)
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': BUCKET, 'Key': supplychain_document},
                                                      ExpiresIn=300)
            return DownloadSupplychainDocument(success=True, presigned_url=str(presigned_url))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteSupplychainDocument(graphene.Mutation):
    supplychainfiles_id = graphene.Int()

    class Arguments:
        data = graphene.List(SupplychainFilesInput, required=True)

    def mutate(self, info, data):

        s3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        i = 0
        for d in data:
            supplychain_document = get_bucket_file_folder(d.supplychain_document)

            delete_supplychain_docuement = SupplychainFilesModel.objects.filter(
                supplychainfiles_id=d.supplychainfiles_id).first()

            delete_supplychain_docuement.deleted = 1

            supplychainfiles_id = d.supplychainfiles_id

            try:
                s3.Object(BUCKET, supplychain_document).delete()
                delete_supplychain_docuement.save()
                i = i + 1
                if i == len(data):
                    return DeleteSupplychainDocument(supplychainfiles_id)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    upload_supplychain_document = UploadSupplychainDocument.Field()
    download_supplychain_document = DownloadSupplychainDocument.Field()
    delete_supplychain_document = DeleteSupplychainDocument.Field()
