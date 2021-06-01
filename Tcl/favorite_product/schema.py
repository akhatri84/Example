from django.utils import timezone

import graphene
from graphene import relay, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql import GraphQLError
from ErrorHandler import send_err_res

from .models import FavoriteProductModel
from product.models import ProductModel
from app_user.models import AppUserModel


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return FavoriteProductModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class FavoriteProductType(DjangoObjectType):
    class Meta:
        model = FavoriteProductModel
        filter_fields = {
            'product': ['exact'],
            'deleted':['exact']
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    favoriteproduct = relay.Node.Field(FavoriteProductType)
    all_favoriteproduct = DjangoFilterConnectionField(FavoriteProductType,
                                                      favoriteproduct_pk=graphene.Int(),
                                                      favoriteproduct_id=graphene.Int(),
                                                      product_id=graphene.Int(),
                                                      orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_favoriteproduct(self, info, favoriteproduct_pk=None, favoriteproduct_id=None, product_id=None,
                                    **kwargs):
        orderBy = kwargs.get('orderBy', None)

        favoriteproduct_search = FavoriteProductModel.objects.all()

        if favoriteproduct_pk:
            favoriteproduct_search = favoriteproduct_search.filter(pk=favoriteproduct_pk)
        if favoriteproduct_id:
            favoriteproduct_search = favoriteproduct_search.filter(favoriteproduct_id=favoriteproduct_id)
        if product_id:
            favoriteproduct_search = favoriteproduct_search.filter(product__product_id__exact=product_id)
        if orderBy:
            favoriteproduct_search = favoriteproduct_search.order_by(*orderBy)
        return favoriteproduct_search


class CreateFavoriteProduct(graphene.relay.ClientIDMutation):
    favoriteproduct = graphene.Field(FavoriteProductType)

    class Input:
        user_id = graphene.Int(required=True)
        product_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):

        favoriteproduct = FavoriteProductModel.objects.filter(product_id=kwargs.get("product_id")).filter(
            user_id_id=kwargs.get("user_id")).first()

        if favoriteproduct == None:
            favoriteproduct = FavoriteProductModel()
            for key, value in kwargs.items():
                if key == 'product_id':
                    product = ProductModel.objects.get(pk=value, deleted=0)

                    if product == None:
                        return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    else:
                        favoriteproduct.product = product

                if key == 'user_id':
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                    if app_user == None:
                        return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    else:
                        favoriteproduct.user_id = app_user
                        favoriteproduct.updated_by = app_user.appusers_id

                favoriteproduct.__dict__[key] = value
        else:
            if favoriteproduct.deleted == 0:
                favoriteproduct.deleted = 1
            else:
                favoriteproduct.deleted = 0

        favoriteproduct.created_at = timezone.now()
        favoriteproduct.updated_at = timezone.now()

        try:
            favoriteproduct.save()
            return CreateFavoriteProduct(favoriteproduct=favoriteproduct)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateFavoriteProduct(graphene.relay.ClientIDMutation):
    favoriteproduct = graphene.Field(FavoriteProductType)

    class Input:
        favoriteproduct_id = graphene.Int(required=True)
        product_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, favoriteproduct_id, **kwargs):
        favoriteproduct_update = FavoriteProductModel.objects.filter(favoriteproduct_id=favoriteproduct_id,
                                                                     deleted=0).first()
        try:
            if favoriteproduct_update != None:
                for key, value in kwargs.items():
                    if key == 'product_id':
                        try:
                            product = ProductModel.objects.get(pk=value, deleted=0)
                        except:
                            product = None
                        favoriteproduct_update.product = product

                    if key == 'user_id':
                        try:
                            app_user = AppUserModel.objects.get(pk=value, deleted=0)
                        except:
                            app_user = None
                        favoriteproduct_update.user_id = app_user


                favoriteproduct_update.updated_at = timezone.now()
                favoriteproduct_update.updated_by = app_user.appusers_id
                favoriteproduct_update.save()
                return UpdateFavoriteProduct(favoriteproduct=favoriteproduct_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteFavoriteProduct(graphene.relay.ClientIDMutation):
    favoriteproduct_id = graphene.Int()

    class Input:
        favoriteproduct_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, favoriteproduct_id):
        delete_favoriteproduct = FavoriteProductModel.objects.filter(
            favoriteproduct_id=favoriteproduct_id).first()
        delete_favoriteproduct.deleted = 1

        try:
            delete_favoriteproduct.save()
            return DeleteFavoriteProduct(favoriteproduct_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_favorite_product = CreateFavoriteProduct.Field()
    update_favorite_product = UpdateFavoriteProduct.Field()
    delete_favorite_product = DeleteFavoriteProduct.Field()
