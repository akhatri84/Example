from django.utils import timezone

import graphene
from graphene import Union, relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res
from email_notification import notify_client
from decouple import config
from django.conf import settings
from django.db.models import Q
import boto3

from .models import AppUserModel

ACCESS_KEY = config('AWS_ACCESS_KEY')
SECRET_KEY = config('AWS_SECRET_KEY')
REGION_NAME = config('REGION_NAME')
BUCKET = config('BUCKET_NAME')


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return AppUserModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class AppUserType(DjangoObjectType):
    class Meta:
        model = AppUserModel
        filter_fields = {
            'first_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'last_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'email': ['exact', 'icontains', 'istartswith', 'contains'],
            'cognito_id': ['exact', 'icontains', 'istartswith', 'contains'],
            'city': ['exact', 'icontains', 'istartswith', 'contains'],
            'country': ['exact', 'icontains', 'istartswith', 'contains'],
            'phone': ['exact', 'icontains', 'istartswith', 'contains'],
            'user_type': ['exact', 'icontains', 'istartswith', 'contains'],
            'newsletter': ['exact'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    appuser = relay.Node.Field(AppUserType)
    all_appuser = DjangoFilterConnectionField(AppUserType, appuser_pk=graphene.Int(), search=graphene.String(),
                                              orderBy=graphene.List(of_type=graphene.String))
    me = graphene.Field(AppUserType)

    def resolve_all_appuser(self, info, appuser_pk=None, search=None, **kwargs):

        orderBy = kwargs.get('orderBy', None)

        appuser_search = AppUserModel.objects.all()

        if appuser_pk:
            appuser_search = appuser_search.filter(pk=appuser_pk)
        if orderBy:
            appuser_search = appuser_search.order_by(*orderBy)
        if search:
            appuser_search = appuser_search.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(cognito_id__icontains=search) |
                Q(city__icontains=search) |
                Q(country__icontains=search) |
                Q(phone__exact=search) |
                Q(user_type__icontains=search)

            )

        return appuser_search

    def resolve_me(self, info):
        print(info.context.__dict__)
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not Logged In')
        return user


class CreateAppUser(graphene.relay.ClientIDMutation):
    appuser = graphene.Field(AppUserType)

    class Input:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        cognito_id = graphene.String()
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String()
        user_type = graphene.String()
        newsletter = graphene.Boolean()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        appuser = AppUserModel()

        for key, value in kwargs.items():
            if key == 'email' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            elif key == 'user_type' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            appuser.__dict__[key] = value

        appuser.created_at = timezone.now()
        appuser.updated_at = timezone.now()
        appuser.updated_by = 1
        appuser.deleted = 0

        try:
            appuser.save()
            return CreateAppUser(appuser=appuser)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateAppUser(graphene.relay.ClientIDMutation):
    appuser = graphene.Field(AppUserType)

    class Input:
        appusers_id = graphene.Int()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        cognito_id = graphene.String()
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String()
        user_type = graphene.String()
        newsletter = graphene.Boolean()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, appusers_id, **kwargs):
        appuser_update = AppUserModel.objects.filter(appusers_id=appusers_id, deleted=0).first()

        print(kwargs)
        try:
            if appuser_update != None:
                for key, value in kwargs.items():
                    if key == 'email' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    elif key == 'user_type' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    setattr(appuser_update, key, value)

                appuser_update.updated_at = timezone.now()
                appuser_update.updated_by = appusers_id
                appuser_update.save()
                return UpdateAppUser(appuser=appuser_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteAppUser(graphene.relay.ClientIDMutation):
    appusers_id = graphene.Int()

    class Input:
        appusers_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, appusers_id):
        delete_appuser = AppUserModel.objects.filter(appusers_id=appusers_id).first()
        delete_appuser.deleted = 1

        try:
            delete_appuser.save()
            return DeleteAppUser(appusers_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_app_user = CreateAppUser.Field()
    update_app_user = UpdateAppUser.Field()
    delete_app_user = DeleteAppUser.Field()
