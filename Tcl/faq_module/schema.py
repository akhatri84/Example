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

from .models import FAQModel
from app_user.models import AppUserModel

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return FAQModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class FAQModelType(DjangoObjectType):
    class Meta:
        model = FAQModel
        filter_fields = {
            'question': ['exact', 'icontains', 'istartswith', 'contains'],
            'answer': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    faq = relay.Node.Field(FAQModelType)
    all_faq = DjangoFilterConnectionField(FAQModelType, faq_pk=graphene.Int(), search=graphene.String(),
                                              orderBy=graphene.List(of_type=graphene.String))
   
    def resolve_all_faq(self, info, faq_pk=None, search=None, **kwargs):

        orderBy = kwargs.get('orderBy', None)

        faq_search = FAQModel.objects.all()

        if faq_pk:
            faq_search = faq_search.filter(pk=faq_pk)
        if orderBy:
            faq_search = faq_search.order_by(*orderBy)
        if search:
            faq_search = faq_search.filter(
                Q(question__icontains=search) |
                Q(answer__icontains=search) 
            )

        return faq_search


class CreateFAQ(graphene.relay.ClientIDMutation):
    faq = graphene.Field(FAQModelType)

    class Input:
        question = graphene.String()
        answer = graphene.String()
        user_id = graphene.Int()
        

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info,user_id, **kwargs):
        faq = FAQModel()
        
        user = AppUserModel.objects.get(pk=user_id,deleted=0)

        for key, value in kwargs.items():
            if key == 'question' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'answer' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            faq.__dict__[key] = value

        faq.created_at = timezone.now()
        faq.updated_at = timezone.now()
        faq.updated_by = user.appusers_id
        faq.deleted = 0

        try:
            faq.save()
            return CreateFAQ(faq=faq)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateFAQ(graphene.relay.ClientIDMutation):
    faq_update = graphene.Field(FAQModelType)
    
    class Input:
        faq_id = graphene.Int()
        question = graphene.String()
        answer = graphene.String()
        user_id = graphene.Int()
        
    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, faq_id,user_id, **kwargs):
       
        user = AppUserModel.objects.get(pk=user_id,deleted=0)

        faq_update = FAQModel.objects.filter(faq_id=faq_id, deleted=0).first()
        try:
            if faq_update != None:
                for key, value in kwargs.items():
                    if key == 'question' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'answer' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    setattr(faq_update, key, value)

                faq_update.updated_at = timezone.now()
                faq_update.updated_by = user.appusers_id
                faq_update.save()
                return UpdateFAQ(faq_update=faq_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            raise
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteFAQ(graphene.relay.ClientIDMutation):
    faq_id = graphene.Int()

    class Input:
        faq_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, faq_id):
        delete_faq = FAQModel.objects.filter(faq_id=faq_id).first()
        delete_faq.deleted = 1

        try:
            delete_faq.save()
            return DeleteFAQ(faq_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass

class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_FAQ = CreateFAQ.Field()
    update_FAQ = UpdateFAQ.Field()
    delete_FAQ = DeleteFAQ.Field()
