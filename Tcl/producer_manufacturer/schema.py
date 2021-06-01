from django.utils import timezone

import graphene
from graphene import Union, relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res

from .models import ProducerManufacturerModel
from supplychain.models import SupplychainModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ProducerManufacturerModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ProducerManufacturerInput(graphene.InputObjectType):
    producermanufacturer_id = graphene.Int()
    supply_chain_id = graphene.Int()
    producer_name = graphene.String()
    process = graphene.String()
    city = graphene.String()
    country = graphene.String()


class ProducerManufacturerType(DjangoObjectType):
    class Meta:
        model = ProducerManufacturerModel
        filter_fields = {
            'producer_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'city': ['exact', 'icontains', 'istartswith', 'contains'],
            'country': ['exact', 'icontains', 'istartswith', 'contains'],
            'deleted': ['exact']
        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    producermanufacturer = relay.Node.Field(ProducerManufacturerType)
    all_producermanufacturer = DjangoFilterConnectionField(ProducerManufacturerType,
                                                           producermanufacturer_pk=graphene.Int(),
                                                           supply_chain_id=graphene.Int(), search=graphene.String(),
                                                           orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_producermanufacturer(self, info, producermanufacturer_pk=None, supply_chain_id=None, search=None,
                                         **kwargs):
        orderBy = kwargs.get('orderBy', None)

        producermanufacturer_search = ProducerManufacturerModel.objects.all()

        if producermanufacturer_pk:
            producermanufacturer_search = producermanufacturer_search.filter(pk=producermanufacturer_pk)
        if supply_chain_id:
            producermanufacturer_search = producermanufacturer_search.filter(supply_chain_id=supply_chain_id)
        if orderBy:
            producermanufacturer_search = producermanufacturer_search.order_by(*orderBy)
        if search:
            producermanufacturer_search = producermanufacturer_search.filter(
                Q(producer_name__icontains=search) |
                Q(city__icontains=search) |
                Q(country__icontains=search)
            )
        return producermanufacturer_search


class CreateProducerManufacturer(graphene.relay.ClientIDMutation):
    producermanufacturer = graphene.Field(ProducerManufacturerType)

    class Input:
        data = graphene.List(ProducerManufacturerInput, required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, data):

        producer_list = []
        for d in data:
            producermanufacturer = ProducerManufacturerModel()
            for key, value in d.items():
                if key == 'producer_name':
                    if len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if len(value.strip()) > 80:
                        raise GraphQLError(send_err_res.raiseError(key, "EL"))
                if key == 'process' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))
                if key == 'city' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))
                if key == 'country' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))
                if key == 'supply_chain_id':
                    try:
                        supplychain = SupplychainModel.objects.get(pk=value, deleted=0)
                    except:
                        supplychain = None
                if key != 'supply_chain_id':
                    producermanufacturer.__dict__[key] = value
                else:
                    if supplychain == None:
                        return GraphQLError(send_err_res.raiseError("Supplychain", "NV"))
                    producermanufacturer.supply_chain_id = supplychain

            producermanufacturer.created_at = timezone.now()
            producermanufacturer.updated_at = timezone.now()
            producermanufacturer.updated_by = supplychain.user_id.appusers_id
            producermanufacturer.deleted = 0
            producer_list.append(producermanufacturer)

        try:
            for producer in producer_list:
                producer.save()
            return CreateProducerManufacturer(producermanufacturer=producermanufacturer)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateProducerManufacturer(graphene.relay.ClientIDMutation):
    producermanufacturer = graphene.Field(ProducerManufacturerType)

    class Input:
        data = graphene.List(ProducerManufacturerInput, required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, producermanufacturer_id, data):
        producer_list = []
        for d in data:
            if 'producermanufacturer_id' in d:
                producermanufacturer_update = ProducerManufacturerModel.objects.filter(
                    producermanufacturer_id=d.producermanufacturer_id).first()
                for key, value in d.items():
                    if key == 'producer_name':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                        if len(value.strip()) > 80:
                            raise GraphQLError(send_err_res.raiseError(key, "EL"))

                    if key == 'supply_chain_id':
                        value = SupplychainModel.objects.get(pk=value, deleted=0)
                        producermanufacturer_update.updated_by = value.user_id.appusers_id

                    if key == 'process' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'city' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'country' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    setattr(producermanufacturer_update, key, value)
                    producermanufacturer_update.updated_at = timezone.now()
                    producer_list.append(producermanufacturer_update)
            else:
                producermanufacturer_update = ProducerManufacturerModel()
                for key, value in d.items():
                    if key == 'producer_name':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                        if len(value.strip()) > 80:
                            raise GraphQLError(send_err_res.raiseError(key, "EL"))
                    if key == 'process':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'city':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'country':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    if key == 'supply_chain_id':
                        try:
                            supplychain = SupplychainModel.objects.get(pk=value, deleted=0)
                        except:
                            supplychain = None

                    if key != 'supply_chain_id':
                        producermanufacturer_update.__dict__[key] = value
                    else:
                        if supplychain == None:
                            return GraphQLError(send_err_res.raiseError("Supplychain", "NV"))
                        producermanufacturer_update.supply_chain_id = supplychain

                producermanufacturer_update.created_at = timezone.now()
                producermanufacturer_update.updated_at = timezone.now()
                producermanufacturer_update.updated_by = supplychain.user_id.appusers_id
                producermanufacturer_update.deleted = 0
                producer_list.append(producermanufacturer_update)

        try:
            for producer in producer_list:
                producer.save()
            return UpdateProducerManufacturer(producermanufacturer=producermanufacturer_update)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteProducerManufacturer(graphene.relay.ClientIDMutation):
    producermanufacturer_id = graphene.Int()

    class Input:
        producermanufacturer_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, producermanufacturer_id):
        delete_producermanufacturer = ProducerManufacturerModel.objects.filter(
            producermanufacturer_id=producermanufacturer_id).first()
        delete_producermanufacturer.deleted = 1

        try:
            delete_producermanufacturer.save()
            return DeleteProducerManufacturer(producermanufacturer_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_producermanufacturer = CreateProducerManufacturer.Field()
    update_producermanufacturer = UpdateProducerManufacturer.Field()
    delete_producermanufacturer = DeleteProducerManufacturer.Field()
