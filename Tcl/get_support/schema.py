from django.utils import timezone
from django.db.models import Q

import graphene
from graphene import Union, relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res
from email_notification import notify_client
from decouple import config

from .models import GetSupportModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return GetSupportModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class GetSupportType(DjangoObjectType):
    class Meta:
        model = GetSupportModel
        filter_fields = {
            'support_content': ['exact', 'icontains', 'istartswith', 'contains'],
            'status': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact'],
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    getsupport = relay.Node.Field(GetSupportType)
    all_getsupport = DjangoFilterConnectionField(GetSupportType, getsupport_pk=graphene.Int(), user_id=graphene.Int(),
                                                 search=graphene.String(),
                                                 orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_getsupport(self, info, getsupport_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        getsupport_search = GetSupportModel.objects.all()

        if getsupport_pk:
            getsupport_search = getsupport_search.filter(pk=getsupport_pk)
        if user_id:
            getsupport_search = getsupport_search.filter(user_id=user_id)
        if orderBy:
            getsupport_search = getsupport_search.order_by(*orderBy)
        if search:
            getsupport_search = getsupport_search.filter(
                Q(support_content__icontains=search) |
                Q(status__icontains=search)
            )

        return getsupport_search


class CreateGetSupport(graphene.relay.ClientIDMutation):
    getsupport = graphene.Field(GetSupportType)

    class Input:
        user_id = graphene.Int(required=True)
        support_content = graphene.String(required=True)
        status = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        getsupport = GetSupportModel()

        for key, value in kwargs.items():
            if key == 'support_content' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                getsupport.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                getsupport.user_id = app_user

        getsupport.created_at = timezone.now()
        getsupport.updated_at = timezone.now()
        getsupport.updated_by = app_user.appusers_id
        getsupport.deleted = 0
        try:
            getsupport.save()
            context = {
                "Support Content": getsupport.support_content,
                "Status": getsupport.status,
            }
            notify_client.sendMailApp(config("ADMIN_EMAIL"), "Support Content", "Add", context)
            return CreateGetSupport(getsupport=getsupport)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateGetSupport(graphene.relay.ClientIDMutation):
    getsupport = graphene.Field(GetSupportType)

    class Input:
        getsupport_id = graphene.Int(required=True)
        user_id = graphene.Int()
        support_content = graphene.String()
        status = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, getsupport_id, **kwargs):
        getsupport_update = GetSupportModel.objects.filter(getsupport_id=getsupport_id, deleted=0).first()

        try:
            if getsupport_update != None:
                for key, value in kwargs.items():
                    if key == 'support_content' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'user_id':
                        try:
                            app_user = AppUserModel.objects.get(pk=value, deleted=0)
                        except:
                            app_user = None

                    if key != 'user_id':
                        setattr(getsupport_update, key, value)
                    else:
                        if app_user == None:
                            return GraphQLError(send_err_res.raiseError("User", "NV"))
                        getsupport_update.user_id = app_user

                getsupport_update.updated_at = timezone.now()
                getsupport_update.updated_by = app_user.appusers_id
                getsupport_update.save()
                context = {
                    "Support Content": getsupport_update.support_content,
                    "Status": getsupport_update.status,
                }
                notify_client.sendMailApp(config("ADMIN_EMAIL"), "Support Content", "Add", context)
                return UpdateGetSupport(getsupport=getsupport_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteGetSupport(graphene.relay.ClientIDMutation):
    getsupport_id = graphene.Int()

    class Input:
        getsupport_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, getsupport_id):
        delete_getsupport = GetSupportModel.objects.filter(getsupport_id=getsupport_id).first()
        delete_getsupport.deleted = 1

        try:
            delete_getsupport.save()
            return DeleteGetSupport(getsupport_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_getsupport = CreateGetSupport.Field()
    update_getsupport = UpdateGetSupport.Field()
    delete_getsupport = DeleteGetSupport.Field()
