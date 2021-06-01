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

from .models import ImpactIndicatorFilesModel
from impact_indicator.models import ImpactIndicatorModel

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
        return ImpactIndicatorFilesModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ImpactIndicatorFilesType(DjangoObjectType):
    class Meta:
        model = ImpactIndicatorFilesModel
        filter_fields = {
            'file_type': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_extension': ['exact', 'icontains', 'istartswith', 'contains'],
            'aws_file_url': ['exact', 'icontains', 'istartswith', 'contains'],
            'file_size': ['exact', 'icontains', 'istartswith', 'contains'],
            'impactindicatorfile_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    impactindicatorfile = relay.Node.Field(ImpactIndicatorFilesType)
    all_impactindicatorfiles = DjangoFilterConnectionField(ImpactIndicatorFilesType,
                                                           impactindicatorfile_pk=graphene.Int(),
                                                           impact_indicator=graphene.Int(), search=graphene.String(),
                                                           orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_impactindicatorfiles(self, info, impactindicatorfile_pk=None, impact_indicator=None, search=None,
                                         **kwargs):
        orderBy = kwargs.get('orderBy', None)

        impactindicatorfile_search = ImpactIndicatorFilesModel.objects.all()

        if impactindicatorfile_pk:
            impactindicatorfile_search = impactindicatorfile_search.filter(pk=impactindicatorfile_pk)
        if impact_indicator:
            impactindicatorfile_search = impactindicatorfile_search.filter(impact_indicator=impact_indicator)
        if orderBy:
            impactindicatorfile_search = impactindicatorfile_search.order_by(*orderBy)
        if search:
            impactindicatorfile_search = impactindicatorfile_search.filter(
                Q(file_type__icontains=search) |
                Q(file_extension__icontains=search) |
                Q(aws_file_url__icontains=search) |
                Q(file_size__icontains=search) |
                Q(impactindicatorfile_name__icontains=search)
            )
        return impactindicatorfile_search


class ImpactIndicatorFileInput(graphene.InputObjectType):
    impactindicatorfiles_id = graphene.Int()
    impactindicator_file = graphene.String()


class UploadImpactIndicatorFile(graphene.Mutation):
    impactindicatorfile = graphene.Field(ImpactIndicatorFilesType)

    class Arguments:
        impactindicator_file = Upload(required=True)
        impact_indicator_id = graphene.Int()

    success = graphene.Boolean()
    presignedUrl = graphene.String()

    def mutate(self, info, impactindicator_file, impact_indicator_id, s3_file=None):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        # for impact_indicator_file in info.context.FILES:
        file_extension = file_extention(str(impactindicator_file))
        file_format = mimetypes.types_map[file_extension]

        if file_extension.lower() not in [".jpg", ".png", ".jpeg", ".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex",
                                          ".txt", ".wpd"]:
            raise GraphQLError(send_err_res.raiseError("Valid File", "NP"))
        else:

            impactindicatorfile = ImpactIndicatorFilesModel()

            try:
                impact_indicator = ImpactIndicatorModel.objects.get(pk=impact_indicator_id, deleted=0)
            except:
                return GraphQLError(send_err_res.raiseError("Impact Indicator", "NV"))


            filename = timezone.now().strftime("%Y%m%d-%H%M%S")
            tempfile = settings.MEDIA_ROOT + default_storage.save(filename + file_extention(str(impactindicator_file)),
                                                                  ContentFile(impactindicator_file.read()))
            s3_file = f"{impact_indicator_id}" + "_impactindicator/" + str(
                impact_indicator_id) + "-" + filename + file_extension
            impactindicatorfile.impact_indicator = impact_indicator
            impactindicatorfile.file_type = "pic"
            impactindicatorfile.file_extension = file_extension
            impactindicatorfile.aws_file_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_file}"
            impactindicatorfile.file_size = str(round((path.getsize(tempfile) / 1000), 1)) + " KB"
            impactindicatorfile.impactindicatorfile_name = str(impactindicator_file)
            impactindicatorfile.created_at = timezone.now()
            impactindicatorfile.updated_at = timezone.now()
            impactindicatorfile.deleted = 0

            try:
                if file_extension.lower() in [".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex", ".txt", ".wpd"]:
                    s3.upload_file(tempfile, BUCKET, s3_file, ExtraArgs={'ACL': 'private', 'ContentType': file_format})
                else:
                    s3.upload_file(tempfile, BUCKET, s3_file,
                                   ExtraArgs={'ACL': 'public-read', 'ContentType': file_format})

                impactindicatorfile.save()

                # create presigned_url
                presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET,
                                                                                'Key': get_bucket_file_folder(
                                                                                    impactindicatorfile.aws_file_url)},
                                                          ExpiresIn=300)

                if os.path.isfile(tempfile):
                    os.remove(tempfile)

                return UploadImpactIndicatorFile(success=True, presignedUrl=presigned_url,
                                         impactindicatorfile=impactindicator_file)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass


class DownloadImpactIndicatorFile(graphene.Mutation):
    class Arguments:
        impactindicator_file = graphene.String()

    success = graphene.Boolean()
    presigned_url = graphene.String()

    def mutate(self, info, impactindicator_file):
        s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY)

        impactindicator_file = get_bucket_file_folder(impactindicator_file)

        try:
            s3.head_object(Bucket=BUCKET, Key=impactindicator_file)
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': BUCKET, 'Key': impactindicator_file},
                                                      ExpiresIn=300)
            return DownloadImpactIndicatorFile(success=True, presigned_url=str(presigned_url))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteImpactIndicatorFile(graphene.Mutation):
    impactindicatorfiles_id = graphene.Int()

    class Arguments:
        data = graphene.List(ImpactIndicatorFileInput, required=True)

    success = graphene.Boolean()

    def mutate(self, info, data):
        s3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        i = 0
        for d in data:

            impactindicator_file = get_bucket_file_folder(d.impactindicator_file)
            delete_impactindicator_file = ImpactIndicatorFilesModel.objects.filter(
                impactindicatorfiles_id=d.impactindicatorfiles_id).first()

            delete_impactindicator_file.deleted = 1

            impactindicatorfiles_id = d.impactindicatorfiles_id
            try:
                s3.Object(BUCKET, impactindicator_file).delete()
                delete_impactindicator_file.save()
                i = i + 1
                if i == len(data):
                    return DeleteImpactIndicatorFile(impactindicatorfiles_id)
            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))
            finally:
                pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    upload_impactindicator_file = UploadImpactIndicatorFile.Field()
    download_impactindicator_file = DownloadImpactIndicatorFile.Field()
    delete_impactindicator_file = DeleteImpactIndicatorFile.Field()
