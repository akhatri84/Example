import sys

sys.path.append('../')

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

from .models import SupplychainModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return SupplychainModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class SupplychainType(DjangoObjectType):
    class Meta:
        model = SupplychainModel
        filter_fields = {
            'supply_chain_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'shipping_transportation_routes_information': ['exact', 'icontains', 'istartswith', 'contains'],
            'gathering_data': ['exact', 'icontains', 'istartswith', 'contains'],
            'social_impact': ['exact', 'icontains', 'istartswith', 'contains'],
            'final_remarks': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact'],
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    """This is root query class."""
    supplychain = relay.Node.Field(SupplychainType)
    all_supplychain = DjangoFilterConnectionField(SupplychainType, supplychain_pk=graphene.Int(),
                                                  user_id=graphene.Int(), search=graphene.String(),
                                                  orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_supplychain(self, info, supplychain_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        supplychain_search = SupplychainModel.objects.all()

        if supplychain_pk:
            supplychain_search = supplychain_search.filter(pk=supplychain_pk)
        if user_id:
            supplychain_search = supplychain_search.filter(user_id=user_id)
        if orderBy:
            supplychain_search = supplychain_search.order_by(*orderBy)
        if search:
            supplychain_search = supplychain_search.filter(
                Q(supply_chain_name__icontains=search) |
                Q(shipping_transportation_routes_information__icontains=search) |
                Q(gathering_data__icontains=search) |
                Q(social_impact__icontains=search) |
                Q(final_remarks__icontains=search)
            )

        return supplychain_search


class CreateSupplychain(graphene.relay.ClientIDMutation):
    supplychain = graphene.Field(SupplychainType)

    class Input:
        user_id = graphene.Int()
        supply_chain_name = graphene.String()
        shipping_transportation_routes_information = graphene.String()
        gathering_data = graphene.String()
        social_impact = graphene.String()
        final_remarks = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):

        supplychain = SupplychainModel()

        for key, value in kwargs.items():
            if key == 'shipping_transportation_routes_information' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                supplychain.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                supplychain.user_id = app_user

        supplychain.user_id = app_user
        supplychain.created_at = timezone.now()
        supplychain.updated_at = timezone.now()
        supplychain.updated_by = app_user.appusers_id
        supplychain.deleted = 0

        try:
            supplychain.save()
            context = {
                "Supply Chain Name": supplychain.supply_chain_name,
            }
            notify_client.sendMailApp(config("ADMIN_EMAIL"), "Supply Chain Name", "Add", context)
            return CreateSupplychain(supplychain=supplychain)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateSupplychain(graphene.relay.ClientIDMutation):
    supplychain = graphene.Field(SupplychainType)

    class Input:
        supplychain_id = graphene.Int(required=True)
        user_id = graphene.Int()
        supply_chain_name = graphene.String()
        shipping_transportation_routes_information = graphene.String()
        gathering_data = graphene.String()
        social_impact = graphene.String()
        final_remarks = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, supplychain_id, **kwargs):
        supplychain_update = SupplychainModel.objects.filter(supplychain_id=supplychain_id, deleted=0).first()

        try:
            if supplychain_update != None:
                for key, value in kwargs.items():
                    if key == 'shipping_transportation_routes_information' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    if key == 'user_id':
                        try:
                            app_user = AppUserModel.objects.get(pk=value, deleted=0)
                        except:
                            app_user = None

                    if key != 'user_id':
                        setattr(supplychain_update, key, value)
                    else:
                        if app_user == None:
                            return GraphQLError(send_err_res.raiseError("User", "NV"))
                        supplychain_update.user_id = app_user

                supplychain_update.updated_at = timezone.now()
                supplychain_update.updated_by = app_user.appusers_id

                supplychain_update.save()
                context = {
                    "Supply Chain Name": supplychain_update.supply_chain_name,
                }
                notify_client.sendMailApp(config("ADMIN_EMAIL"), "Supply Chain Name", "Update", context)
                return UpdateSupplychain(supplychain=supplychain_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteSupplychain(graphene.relay.ClientIDMutation):
    supplychain_id = graphene.Int()

    class Input:
        supplychain_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, supplychain_id):
        delete_supplychain = SupplychainModel.objects.filter(supplychain_id=supplychain_id).first()
        delete_supplychain.deleted = 1

        try:
            context = {
                "Supply Chain Name": delete_supplychain.supply_chain_name,
            }
            delete_supplychain.save()
            notify_client.sendMailApp(config("ADMIN_EMAIL"), "Supply Chain Name", "Delete", context)
            return DeleteSupplychain(supplychain_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_supplychain = CreateSupplychain.Field()
    update_supplychain = UpdateSupplychain.Field()
    delete_supplychain = DeleteSupplychain.Field()
