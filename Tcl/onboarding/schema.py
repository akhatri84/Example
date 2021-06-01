import sys
import re

sys.path.append('../')

from django.utils import timezone

import graphene
from graphene import Union, relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res

from .models import OnboardingModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info, *args):
        return OnboardingModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class OnboardingType(DjangoObjectType):
    class Meta:
        model = OnboardingModel
        filter_fields = {
            'company': ['exact', 'icontains', 'istartswith', 'contains'],
            'website': ['exact', 'icontains', 'istartswith', 'contains'],
            'about_brand': ['exact', 'icontains', 'istartswith', 'contains'],
            'remarks': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact'],
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    """This is root query class."""
    vendor = relay.Node.Field(OnboardingType)
    all_vendors = DjangoFilterConnectionField(OnboardingType, onboarding_pk=graphene.Int(), user_id=graphene.Int(),
                                              search=graphene.String(),
                                              orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_vendors(self, info, onboarding_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        vendor_search = OnboardingModel.objects.all()

        if onboarding_pk:
            vendor_search = vendor_search.filter(pk=onboarding_pk)
        if user_id:
            vendor_search = vendor_search.filter(user_id=user_id)
        if orderBy:
            vendor_search = vendor_search.order_by(*orderBy)
        if search:
            vendor_search = vendor_search.filter(
                Q(company__icontains=search) |
                Q(website__icontains=search) |
                Q(about_brand__icontains=search) |
                Q(remarks__icontains=search)
            )
        return vendor_search


class CreateVendor(graphene.relay.ClientIDMutation):
    vendor = graphene.Field(OnboardingType)

    class Input:
        user_id = graphene.Int(required=True)
        company = graphene.String()
        website = graphene.String()
        about_brand = graphene.String()
        remarks = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):

        vendor = OnboardingModel()

        for key, value in kwargs.items():
            if key in ['company', 'website'] and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            elif key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                vendor.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                vendor.user_id = app_user

        vendor.created_at = timezone.now()
        vendor.updated_at = timezone.now()
        vendor.updated_by = app_user.appusers_id
        vendor.deleted = 0

        try:
            vendor.save()
            return CreateVendor(vendor=vendor)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateVendor(graphene.relay.ClientIDMutation):
    vendor = graphene.Field(OnboardingType)

    class Input:
        onboarding_id = graphene.Int(required=True)
        user_id = graphene.Int()
        company = graphene.String()
        website = graphene.String()
        about_brand = graphene.String()
        remarks = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, onboarding_id, **kwargs):

        vendor_update = OnboardingModel.objects.filter(onboarding_id=onboarding_id).first()

        for key, value in kwargs.items():
            if key in ['company', 'website'] and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                setattr(vendor_update, key, value)
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                vendor_update.user_id = app_user

        vendor_update.updated_at = timezone.now()
        vendor_update.updated_by = app_user.appusers_id

        try:
            vendor_update.save()
            return UpdateVendor(vendor=vendor_update)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteVendor(graphene.relay.ClientIDMutation):
    """This mutation is to delete user in the database."""
    vendor_id = graphene.Int()

    class Input:
        vendor_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, vendor_id):
        delete_vendor = OnboardingModel.objects.filter(onboarding_id=vendor_id).first()
        delete_vendor.deleted = 1

        try:
            delete_vendor.save()
            return DeleteVendor(vendor_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_vendor = CreateVendor.Field()
    update_vendor = UpdateVendor.Field()
    delete_vendor = DeleteVendor.Field()
