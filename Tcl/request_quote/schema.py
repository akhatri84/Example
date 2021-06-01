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

from .models import RequestQuoteModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return RequestQuoteModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class RequestQuoteType(DjangoObjectType):
    class Meta:
        model = RequestQuoteModel
        filter_fields = {
            'quote_content': ['exact', 'icontains', 'istartswith', 'contains'],
            'status': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']

        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    """This is root query class."""
    requestquote = relay.Node.Field(RequestQuoteType)
    all_request_quotes = DjangoFilterConnectionField(RequestQuoteType, requestquote_pk=graphene.Int(),
                                                     user_id=graphene.Int(), search=graphene.String(),
                                                     orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_request_quotes(self, info, requestquote_pk=None, user_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        requestquote_search = RequestQuoteModel.objects.all()

        if requestquote_pk:
            requestquote_search = requestquote_search.filter(pk=requestquote_pk)
        if user_id:
            requestquote_search = requestquote_search.filter(user_id=user_id)
        if orderBy:
            requestquote_search = requestquote_search.order_by(*orderBy)
        if search:
            requestquote_search = requestquote_search.filter(
                Q(quote_content__icontains=search) |
                Q(status__icontains=search)
            )

        return requestquote_search


class CreateRequestQuote(graphene.relay.ClientIDMutation):
    requestquote = graphene.Field(RequestQuoteType)

    class Input:
        user_id = graphene.Int()
        quote_content = graphene.String()
        status = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):

        requestquote = RequestQuoteModel()

        for key, value in kwargs.items():
            if key == 'quote_content' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                requestquote.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                requestquote.user_id = app_user

        requestquote.created_at = timezone.now()
        requestquote.updated_at = timezone.now()
        requestquote.updated_by = app_user.appusers_id
        requestquote.deleted = 0

        try:
            requestquote.save()
            context = {
                "Quote Content": requestquote.quote_content,
                "Status": requestquote.status,
            }
            notify_client.sendMailApp(config("ADMIN_EMAIL"), "Quote Content", "Add", context)
            return CreateRequestQuote(requestquote=requestquote)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateRequestQuote(graphene.relay.ClientIDMutation):
    requestquote = graphene.Field(RequestQuoteType)

    class Input:
        request_quote_id = graphene.Int(required=True)
        user_id = graphene.Int()
        quote_content = graphene.String()
        status = graphene.String()

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, request_quote_id, **kwargs):

        requestquote_update = RequestQuoteModel.objects.filter(request_quote_id=request_quote_id).first()

        for key, value in kwargs.items():
            if key == 'quote_content' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None

            if key != 'user_id':
                setattr(requestquote_update, key, value)
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                requestquote_update.user_id = app_user

        requestquote_update.updated_at = timezone.now()
        requestquote_update.updated_by = app_user.appusers_id

        try:
            requestquote_update.save()
            context = {
                "Quote Content": requestquote_update.quote_content,
                "Status": requestquote_update.status,
            }
            notify_client.sendMailApp(config("ADMIN_EMAIL"), "Quote Content", "Add", context)
            return UpdateRequestQuote(requestquote=requestquote_update)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteRequestQuote(graphene.relay.ClientIDMutation):
    request_quote_id = graphene.Int()

    class Input:
        request_quote_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, request_quote_id):
        delete_requestquote = RequestQuoteModel.objects.filter(request_quote_id=request_quote_id).first()
        delete_requestquote.deleted = 1

        try:
            delete_requestquote.save()
            return DeleteRequestQuote(request_quote_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_requestquote = CreateRequestQuote.Field()
    update_requestquote = UpdateRequestQuote.Field()
    delete_requestquote = DeleteRequestQuote.Field()
