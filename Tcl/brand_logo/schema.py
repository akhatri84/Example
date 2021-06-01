# System imports
import sys
from pathlib import Path
from django.conf import settings
import os
from os import path
import random
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Q

sys.path.append('../')

# Third party Library Imports
from decouple import config, Csv
import boto3
from botocore.exceptions import NoCredentialsError
import graphene
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res
from urllib.parse import urlparse
from PIL import Image

# Project Imports
from ErrorHandler import send_err_res
from .models import BrandLogoModel
from app_user.models import AppUserModel

import base64

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
        return BrandLogoModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class BrandLogoType(DjangoObjectType):
    class Meta:
        model = BrandLogoModel
        filter_fields = {
            'file_type': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_extension': ['exact', 'icontains', 'istartswith', 'contains'],
            'aws_file_url': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_size': ['exact'],
            'deleted': ['exact'],
            'brandlogo_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'thumb_awsurl': ['exact', 'icontains', 'istartswith', 'contains'],
            'thumb_name': ['exact', 'icontains', 'istartswith', 'contains'],
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    brand_logo = relay.Node.Field(BrandLogoType)
    all_brandlogos = DjangoFilterConnectionField(BrandLogoType, brandlogo_pk=graphene.Int(), user_id=graphene.Int(),
                                                 company=graphene.String(), search=graphene.String(),
                                                 orderBy=graphene.List(of_type=graphene.String))

    brandlogo_search = graphene.List(BrandLogoType)

    def resolve_all_brandlogos(self, info, brandlogo_pk=None, user_id=None, company=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        brandlogo_search = BrandLogoModel.objects.all()

        if brandlogo_pk:
            brandlogo_search = brandlogo_search.filter(pk=brandlogo_pk)
        if user_id:
            brandlogo_search = brandlogo_search.filter(user_id=user_id)
        if company:
            brandlogo_search = brandlogo_search.filter(user_id__onboardingmodel__company__icontains=company)
        if orderBy:
            brandlogo_search = brandlogo_search.order_by(*orderBy)
        if search:
            brandlogo_search = brandlogo_search.filter(
                Q(file_type__icontains=search) |
                Q(file_extension__icontains=search) |
                Q(aws_file_url__icontains=search) |
                Q(file_size__exact=search) |
                Q(brandlogo_name__icontains=search) |
                Q(thumb_awsurl__icontains=search) |
                Q(thumb_name__icontains=search)
            )
        return brandlogo_search


class UploadBrandLogo(graphene.Mutation):
    brand_logo = graphene.Field(BrandLogoType)

    class Arguments:
        brand_logo_file = Upload(required=True)
        s3_file = graphene.String()
        user_id = graphene.Int()

    success = graphene.Boolean()
    presignedUrl = graphene.String()
    thumbnailPresignedUrl = graphene.String()

    def mutate(self, info, brand_logo_file, user_id, s3_file=None):

        old_brand_logo_file = None
        old_thumb_file = None

        # create s3 bucket object
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        file_extension = file_extention(str(brand_logo_file))

        try:

            if file_extension.lower() not in [".jpg", ".png", ".jpeg"]:
                raise GraphQLError(send_err_res.raiseError("Valid File", "NP"))
            else:
                try:
                    app_user = AppUserModel.objects.get(pk=user_id, deleted=0)
                except:
                    app_user = None

                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))

                brand_logo = BrandLogoModel.objects.filter(user_id=app_user.appusers_id, deleted=0).first()
                if brand_logo == None:
                    brand_logo = BrandLogoModel()
                else:
                    old_brand_logo_file = get_bucket_file_folder(brand_logo.aws_file_url)
                    old_thumb_file = get_bucket_file_folder(brand_logo.thumb_awsurl)

                filename = timezone.now().strftime("%Y%m%d-%H%M%S")

                # create thumbnail image and save it as temp thumbnail file
                brand_logo_thumb = Image.open(brand_logo_file)
                picture_format = 'image/' + brand_logo_thumb.format.lower()

                brand_logo_thumb.thumbnail((90, 90), Image.ANTIALIAS)
                thumbnail_tempfile = settings.MEDIA_ROOT + filename + "-thumb" + file_extention(str(brand_logo_file))
                brand_logo_thumb.save(thumbnail_tempfile)

                # create comparessed temp file
                main_brand_logo_file = Image.open(brand_logo_file)
                tempfile = settings.MEDIA_ROOT + filename + file_extention(str(brand_logo_file))
                main_brand_logo_file.save(tempfile, optimize=True, quality=10)

                # tempfile = settings.MEDIA_ROOT + default_storage.save(filename+file_extention(str(brand_logo_file)), ContentFile(brand_logo_file.read()))

                s3_file = f"{app_user.appusers_id}" + "_brand/" + str(
                    app_user.appusers_id) + "-" + filename + file_extension
                s3_thumb = f"{app_user.appusers_id}" + "_brand/" + str(
                    app_user.appusers_id) + "-" + filename + "-thumb" + file_extension

                brand_logo.user_id = app_user
                brand_logo.file_type = "pic"
                brand_logo.file_extension = file_extension
                brand_logo.aws_file_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_file}"
                brand_logo.file_size = str(round((os.path.getsize(tempfile) / 1000), 1)) + " KB"
                brand_logo.brandlogo_name = str(brand_logo_file)
                brand_logo.thumb_awsurl = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_thumb}"
                brand_logo.thumb_name = str(app_user.appusers_id) + "-" + filename + "-thumb" + file_extension
                brand_logo.created_at = timezone.now()
                brand_logo.updated_at = timezone.now()
                brand_logo.updated_by = app_user.appusers_id
                brand_logo.deleted = 0

                # Uploading file to S3 bucket
            s3.upload_file(tempfile, BUCKET, s3_file, ExtraArgs={'ACL': 'public-read', 'ContentType': picture_format})
            s3.upload_file(thumbnail_tempfile, BUCKET, s3_thumb,
                           ExtraArgs={'ACL': 'public-read', 'ContentType': picture_format})

            brand_logo.save()

            # Remove uploaded file from local storage
            if os.path.isfile(tempfile):
                os.remove(tempfile)
            if os.path.isfile(thumbnail_tempfile):
                os.remove(thumbnail_tempfile)

            # create presigned_url for file and thumbnail
            presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET,
                                                                            'Key': get_bucket_file_folder(
                                                                                brand_logo.aws_file_url)},
                                                      ExpiresIn=300)

            thumnail_presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET,
                                                                                     'Key': get_bucket_file_folder(
                                                                                         brand_logo.thumb_awsurl)},
                                                               ExpiresIn=300)

            # Remove old files from s3 buckets
            if old_brand_logo_file != None:
                s3.delete_object(Bucket=BUCKET, Key=get_bucket_file_folder(old_brand_logo_file))
                s3.delete_object(Bucket=BUCKET, Key=get_bucket_file_folder(old_thumb_file))
            return UploadBrandLogo(success=True, presignedUrl=presigned_url,
                                   thumbnailPresignedUrl=thumnail_presigned_url, brand_logo=brand_logo)

        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DownloadBrandLogo(graphene.Mutation):
    class Arguments:
        brand_logo_file = graphene.String()

    success = graphene.Boolean()
    presigned_url = graphene.String()

    def mutate(self, info, brand_logo_file):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)
        brand_logo_file = get_bucket_file_folder(brand_logo_file)

        try:
            s3.head_object(Bucket=BUCKET, Key=brand_logo_file)
            presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': brand_logo_file},
                                                      ExpiresIn=300)
            return DownloadBrandLogo(success=True, presigned_url=str(presigned_url))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteBrandLogo(graphene.Mutation):
    brandlogo_id = graphene.Int()

    class Arguments:
        brandlogo_id = graphene.Int(required=True)
        brand_logo_file = graphene.String()

    def mutate(self, info, brandlogo_id, brand_logo_file):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)
        brand_logo_file = get_bucket_file_folder(brand_logo_file)

        delete_brand_logo_file = BrandLogoModel.objects.filter(brandlogo_id=brandlogo_id).first()
        s3_thumbnail_url = get_bucket_file_folder(delete_brand_logo_file.thumb_awsurl)
        delete_brand_logo_file.deleted = 1

        try:
            s3.delete_object(Bucket=BUCKET, Key=s3_thumbnail_url)
            s3.delete_object(Bucket=BUCKET, Key=brand_logo_file)
            delete_brand_logo_file.save()
            return DeleteBrandLogo(brandlogo_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    uploadBrandLogo = UploadBrandLogo.Field()
    download_brand_logo = DownloadBrandLogo.Field()
    delete_brand_logo = DeleteBrandLogo.Field()
