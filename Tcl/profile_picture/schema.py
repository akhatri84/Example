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
import io

sys.path.append('../')

# Third party Library Imports
from decouple import config, Csv
import graphene
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from urllib.parse import urlparse
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError

import base64

# Project Imports
from ErrorHandler import send_err_res
from .models import ProfilePictureModel
from app_user.models import AppUserModel

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
        return ProfilePictureModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ProfilePictureType(DjangoObjectType):
    class Meta:
        model = ProfilePictureModel
        filter_fields = {
            'file_type': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_extension': ['exact', 'icontains', 'istartswith', 'contains'],
            'aws_file_url': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_size': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact'],
            'profilepicture_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'thumb_awsurl': ['exact', 'icontains', 'istartswith', 'contains'],
            'thumb_name': ['exact', 'icontains', 'istartswith', 'contains'],
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    profile_picture = relay.Node.Field(ProfilePictureType)
    all_profilepictures = DjangoFilterConnectionField(ProfilePictureType, profilepicture_pk=graphene.Int(),
                                                      user_id=graphene.Int(), search=graphene.String(),
                                                      orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_profilepictures(self, info, profilepicture_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        profilepicture_search = ProfilePictureModel.objects.all()

        if profilepicture_pk:
            profilepicture_search = profilepicture_search.filter(pk=profilepicture_pk)
        if user_id:
            profilepicture_search = profilepicture_search.filter(user_id=user_id, deleted=0)
        if orderBy:
            profilepicture_search = profilepicture_search.order_by(*orderBy)
        if search:
            profilepicture_search = profilepicture_search.filter(
                Q(file_type__icontains=search) |
                Q(file_extension__icontains=search) |
                Q(aws_file_url__icontains=search) |
                Q(file_size__icontains=search) |
                Q(profilepicture_name__icontains=search) |
                Q(thumb_awsurl__icontains=search) |
                Q(thumb_name__icontains=search)
            )
        return profilepicture_search


class UploadProfilePicture(graphene.Mutation):
    profile_picture = graphene.Field(ProfilePictureType)

    class Arguments:
        picture_file = Upload(required=True)
        s3_file = graphene.String()
        user_id = graphene.Int()

    success = graphene.Boolean()
    presignedUrl = graphene.String()
    thumbnailPresignedUrl = graphene.String()

    def mutate(self, info, picture_file, user_id, s3_file=None):

        old_profile_file = None
        old_thumb_file = None
        # create s3 bucket object
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        file_extension = file_extention(str(picture_file))

        if file_extension.lower() not in [".jpg", ".png", ".jpeg"]:
            raise GraphQLError(send_err_res.raiseError("Valid File", "NP"))
        else:
            try:
                app_user = AppUserModel.objects.get(pk=user_id, deleted=0)
            except:
                app_user = None

            if app_user == None:
                return GraphQLError(send_err_res.raiseError("User", "NV"))

            profile_picture = ProfilePictureModel.objects.filter(user_id=app_user.appusers_id, deleted=0).first()

            if profile_picture == None:
                profile_picture = ProfilePictureModel()
            else:
                old_profile_file = get_bucket_file_folder(profile_picture.aws_file_url)
                old_thumb_file = get_bucket_file_folder(profile_picture.thumb_awsurl)

            filename = timezone.now().strftime("%Y%m%d-%H%M%S")

            # create Thumbnail image and save it as temp thumbnail file
            picture_file_thumb = Image.open(picture_file)
            picture_format = 'image/' + picture_file_thumb.format.lower()
            picture_file_thumb.thumbnail((90, 90), Image.ANTIALIAS)
            thumbnail_tempfile = settings.MEDIA_ROOT + filename + "-thumb" + file_extention(str(picture_file))
            picture_file_thumb.save(thumbnail_tempfile)

            # create comparessed temp file
            main_picture_file = Image.open(picture_file)
            tempfile = settings.MEDIA_ROOT + filename + file_extention(str(picture_file))
            main_picture_file.save(tempfile, optimize=True, quality=10)

            # tempfile = settings.MEDIA_ROOT + default_storage.save(filename + file_extention(str(picture_file)),
            #                                                      ContentFile(picture_file.read()))

            s3_file = f"{app_user.appusers_id}" + "_user/" + str(app_user.appusers_id) + "-" + filename + file_extension
            s3_thumb = f"{app_user.appusers_id}" + "_user/" + str(
                app_user.appusers_id) + "-" + filename + "-thumb" + file_extension

            profile_picture.user_id = app_user
            profile_picture.file_type = "pic"
            profile_picture.file_extension = file_extension
            profile_picture.aws_file_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_file}"
            profile_picture.file_size = str(round((os.path.getsize(tempfile) / 1000), 1)) + " KB"
            profile_picture.profilepicture_name = str(picture_file)
            profile_picture.thumb_awsurl = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_thumb}"
            profile_picture.thumb_name = str(user_id) + "-" + filename + "-thumb" + file_extension
            profile_picture.created_at = timezone.now()
            profile_picture.updated_at = timezone.now()
            profile_picture.updated_by = app_user.appusers_id
            profile_picture.deleted = 0

            try:
                # Uploading file to S3 bucket
                s3.upload_file(tempfile, BUCKET, s3_file,
                               ExtraArgs={'ACL': 'public-read', 'ContentType': picture_format})
                s3.upload_file(thumbnail_tempfile, BUCKET, s3_thumb,
                               ExtraArgs={'ACL': 'public-read', 'ContentType': picture_format})

                profile_picture.save()

                if os.path.isfile(tempfile):
                    os.remove(tempfile)

                if os.path.isfile(thumbnail_tempfile):
                    os.remove(thumbnail_tempfile)

                # create presigned_url for file and thumbnail
                presigned_url = s3.generate_presigned_url('get_object',
                                                          Params={'Bucket': BUCKET, 'Key': get_bucket_file_folder(
                                                              profile_picture.aws_file_url)},
                                                          ExpiresIn=300)

                thumnail_presigned_url = s3.generate_presigned_url('get_object',
                                                                   Params={'Bucket': BUCKET,
                                                                           'Key': get_bucket_file_folder(
                                                                               profile_picture.thumb_awsurl)},
                                                                   ExpiresIn=300)
                profile_picture.thumnail_presigned_url = thumnail_presigned_url
                # Remove old files from s3 buckets
                if old_profile_file != None:
                    s3.delete_object(Bucket=BUCKET, Key=get_bucket_file_folder(old_profile_file))
                    s3.delete_object(Bucket=BUCKET, Key=get_bucket_file_folder(old_thumb_file))
                return UploadProfilePicture(success=True, presignedUrl=presigned_url,
                                            thumbnailPresignedUrl=thumnail_presigned_url,
                                            profile_picture=profile_picture)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass


class DownloadProfilePicture(graphene.Mutation):
    class Arguments:
        profile_file = graphene.String()

    success = graphene.Boolean()
    presigned_url = graphene.String()

    def mutate(self, info, profile_file):

        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        profile_file = get_bucket_file_folder(profile_file)
        try:
            s3.head_object(Bucket=BUCKET, Key=profile_file)
            presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': profile_file},
                                                      ExpiresIn=300)
            return DownloadProfilePicture(success=True, presigned_url=str(presigned_url))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteProfilePicture(graphene.Mutation):
    profilepictures_id = graphene.Int()

    class Arguments:
        profilepictures_id = graphene.Int(required=True)
        profile_file = graphene.String()

    def mutate(self, info, profilepictures_id, profile_file):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)
        profile_file = get_bucket_file_folder(profile_file)

        delete_profile_file = ProfilePictureModel.objects.filter(profilepictures_id=profilepictures_id).first()
        s3_thumbnail_url = get_bucket_file_folder(delete_profile_file.thumb_awsurl)

        delete_profile_file.deleted = 1

        try:
            s3.delete_object(Bucket=BUCKET, Key=profile_file)
            s3.delete_object(Bucket=BUCKET, Key=s3_thumbnail_url)
            delete_profile_file.save()
            return DeleteProfilePicture(profilepictures_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    upload_profile_picture = UploadProfilePicture.Field()
    download_profile_picture = DownloadProfilePicture.Field()
    delete_profile_picture = DeleteProfilePicture.Field()
