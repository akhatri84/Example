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
from django.db.models import Q

from .models import ApiConfigModel
from app_user.models import AppUserModel
from base64 import b64decode


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ApiConfigModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ApiConfigType(DjangoObjectType):
    class Meta:
        model = ApiConfigModel
        filter_fields = {
            'api_key': ['exact', 'icontains', 'istartswith', 'contains'],
            'secret_key': ['exact', 'icontains', 'istartswith', 'contains'],
            'apiend_point': ['exact', 'icontains', 'istartswith', 'contains'],
            'platform': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    """This is root query class."""
    apiconfig = relay.Node.Field(ApiConfigType)
    all_api_config = DjangoFilterConnectionField(ApiConfigType, apiconfig_pk=graphene.Int(), user_id=graphene.Int(),
                                                 search=graphene.String(),
                                                 orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_api_config(self, info, apiconfig_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        apiconfig_search = ApiConfigModel.objects.all()

        if apiconfig_pk:
            apiconfig_search = apiconfig_search.filter(pk=apiconfig_pk)
        if user_id:
            apiconfig_search = apiconfig_search.filter(user_id=user_id)
        if orderBy:
            apiconfig_search = apiconfig_search.order_by(*orderBy)
        if search:
            apiconfig_search = apiconfig_search.filter(
                Q(api_key__exact=search) |
                Q(secret_key__icontains=search) |
                Q(apiend_point__icontains=search) |
                Q(platform__icontains=search)
            )

        return apiconfig_search


class CreateApiConfig(graphene.relay.ClientIDMutation):
    apiconfig = graphene.Field(ApiConfigType)

    class Input:
        user_id = graphene.Int()
        api_key = graphene.String(required=True)
        secret_key = graphene.String(required=True)
        pwd = graphene.String()
        apiend_point = graphene.String()
        platform = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):

        apiconfig = ApiConfigModel()

        for key, value in kwargs.items():
            if key == 'api_key' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None
            elif key == 'secret_key' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key != 'user_id':
                apiconfig.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                apiconfig.user_id = app_user

        apiconfig.created_at = timezone.now()
        apiconfig.updated_at = timezone.now()
        apiconfig.updated_by = app_user.appusers_id
        apiconfig.deleted = 0

        try:
            apiconfig.save()
            return CreateApiConfig(apiconfig=apiconfig)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateApiConfig(graphene.relay.ClientIDMutation):
    apiconfig = graphene.Field(ApiConfigType)

    class Input:
        apiconfig_id = graphene.Int(required=True)
        user_id = graphene.Int()
        api_key = graphene.String()
        secret_key = graphene.String()
        pwd = graphene.String()
        apiend_point = graphene.String()
        platform = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, apiconfig_id, **kwargs):

        apiconfig_update = ApiConfigModel.objects.filter(apiconfig_id=apiconfig_id, deleted=0).first()

        try:
            if apiconfig_update != None:
                for key, value in kwargs.items():
                    if key == 'api_key' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'user_id':
                        try:
                            app_user = AppUserModel.objects.get(pk=value, deleted=0)
                        except:
                            app_user = None
                    elif key == 'secret_key' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    if key != 'user_id':
                        setattr(apiconfig_update, key, value)
                    else:
                        if app_user == None:
                            return GraphQLError(send_err_res.raiseError("User", "NV"))
                        apiconfig_update.user_id = app_user

                apiconfig_update.updated_at = timezone.now()
                apiconfig_update.updated_by = app_user.appusers_id
                apiconfig_update.save()
                return UpdateApiConfig(apiconfig=apiconfig_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            #return GraphQLError(send_err_res.raiseDBError("SW"))
            raise
        finally:
            pass


class DeleteApiConfig(graphene.relay.ClientIDMutation):
    apiconfig_id = graphene.Int()

    class Input:
        apiconfig_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, apiconfig_id):
        delete_apiconfig = ApiConfigModel.objects.filter(apiconfig_id=apiconfig_id).first()
        delete_apiconfig.deleted = 1

        try:
            delete_apiconfig.save()
            return DeleteApiConfig(apiconfig_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_apiconfig = CreateApiConfig.Field()
    update_apiconfig = UpdateApiConfig.Field()
    delete_apiconfig = DeleteApiConfig.Field()
