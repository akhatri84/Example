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

from .models import ImpactIndicatorModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ImpactIndicatorModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ImpactIndicatorType(DjangoObjectType):
    class Meta:
        model = ImpactIndicatorModel
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith', 'contains'],
            'blog_title': ['exact', 'icontains', 'istartswith', 'contains'],
            'blog_subject': ['exact', 'icontains', 'istartswith', 'contains'],
            'description': ['exact', 'icontains', 'istartswith', 'contains'],
            'blog_description': ['exact', 'icontains', 'istartswith', 'contains'],
            'url': ['exact', 'icontains', 'istartswith', 'contains'],
            'shop_now_url': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    impact_indicator = relay.Node.Field(ImpactIndicatorType)
    all_impact_indicator = DjangoFilterConnectionField(ImpactIndicatorType, impact_indicator_pk=graphene.Int(),
                                                       search=graphene.String(),
                                                       orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_impact_indicator(self, info, impact_indicator_pk=None, search=None, **kwargs):

        orderBy = kwargs.get('orderBy', None)

        impact_indicator_search = ImpactIndicatorModel.objects.all()

        if impact_indicator_pk:
            impact_indicator_search = impact_indicator_search.filter(pk=impact_indicator_pk)
        if orderBy:
            impact_indicator_search = impact_indicator_search.order_by(*orderBy)
        if search:
            impact_indicator_search = impact_indicator_search.filter(
                Q(title__icontains=search) |
                Q(blog_title__icontains=search) |
                Q(blog_subject__icontains=search) |
                Q(description__icontains=search) |
                Q(blog_description__icontains=search) |
                Q(brands_doing__icontains=search) |
                Q(url__icontains=search)|
                Q(shop_now_url__icontains=search)
            )
        return impact_indicator_search


class CreateImpactIndicator(graphene.relay.ClientIDMutation):
    impact_indicator = graphene.Field(ImpactIndicatorType)

    class Input:
        title = graphene.String()
        blog_title = graphene.String()
        blog_subject = graphene.String()
        description = graphene.String()
        blog_description = graphene.String()
        url = graphene.String()
        shop_now_url = graphene.String()
        user_id = graphene.Int()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, user_id, **kwargs):

        impact_indicator = ImpactIndicatorModel()

        user = AppUserModel.objects.get(pk=user_id, deleted=0)

        for key, value in kwargs.items():
            if key == 'title' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'description' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            impact_indicator.__dict__[key] = value

        impact_indicator.created_at = timezone.now()
        impact_indicator.updated_at = timezone.now()
        impact_indicator.updated_by = user.appusers_id
        impact_indicator.deleted = 0

        try:
            impact_indicator.save()
            return CreateImpactIndicator(impact_indicator=impact_indicator)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateImpactIndicator(graphene.relay.ClientIDMutation):
    impact_indicator_update = graphene.Field(ImpactIndicatorType)

    class Input:
        impact_indicator_id = graphene.Int()
        title = graphene.String()
        blog_title = graphene.String()
        blog_subject = graphene.String()
        description = graphene.String()
        blog_description = graphene.String()
        url = graphene.String()
        shop_now_url = graphene.String()
        user_id = graphene.Int()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, impact_indicator_id, user_id, **kwargs):

        impact_indicator_update = ImpactIndicatorModel.objects.filter(impact_indicator_id=impact_indicator_id,
                                                                      deleted=0).first()

        user = AppUserModel.objects.get(pk=user_id, deleted=0)

        try:
            if impact_indicator_update != None:
                for key, value in kwargs.items():
                    if key == 'title' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'description' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    setattr(impact_indicator_update, key, value)

                impact_indicator_update.updated_at = timezone.now()
                impact_indicator_update.updated_by = user.appusers_id
                impact_indicator_update.save()
                return UpdateImpactIndicator(impact_indicator_update=impact_indicator_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            raise
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteImpactIndicator(graphene.relay.ClientIDMutation):
    impact_indicator_id = graphene.Int()

    class Input:
        impact_indicator_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, impact_indicator_id):
        impact_indicator_delete = ImpactIndicatorModel.objects.filter(impact_indicator_id=impact_indicator_id).first()
        impact_indicator_delete.deleted = 1

        try:
            impact_indicator_delete.save()
            return DeleteImpactIndicator(impact_indicator_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_impact_indicator = CreateImpactIndicator.Field()
    update_impact_indicator = UpdateImpactIndicator.Field()
    delete_impact_indicator = DeleteImpactIndicator.Field()
