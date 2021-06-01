import graphene
from django.utils import timezone
from graphene import relay, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ErrorHandler import send_err_res
from product.models import ProductModel,AttributeValueModel
from productwtpsize.models import ProductWtpSizeModel


class ProductWtpSizeConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ProductWtpSizeModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ProductWtpSizeInput(graphene.InputObjectType):
    productwtpsize_id = graphene.Int()
    product_id = graphene.Int()
    size_weight = graphene.String()
    attribute_value_id=graphene.Int()


class ProductWtpSizeType(DjangoObjectType):
    class Meta:
        model = ProductWtpSizeModel
        filter_fields = {'size_weight': ['exact'], 'deleted': ['exact'], }
        interfaces = (relay.Node,)
        connection_class = ProductWtpSizeConnection


class Query(graphene.ObjectType):
    product_wt_p_size = relay.Node.Field(ProductWtpSizeType)
    all_product_wt_p_size = DjangoFilterConnectionField(ProductWtpSizeType,product_id=graphene.Int())

    def resolve_all_product_wt_p_size(self,info,product_id=None,**kwargs):
        product_wtp_size=ProductWtpSizeModel.objects.all()

        if product_id:
            product_wtp_size=product_wtp_size.filter(product_id=product_id)

        return product_wtp_size


class CreateProductWtpSize(graphene.relay.ClientIDMutation):
    productwtpsize = graphene.Field(ProductWtpSizeType)

    class Input:
        data = graphene.List(ProductWtpSizeInput, required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        product_wt_p_size_list = []
        for d in data:
            productwtpsize = ProductWtpSizeModel()
            for key, value in d.items():
                if key == 'size_weight' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))

                if key=='attribute_value_id':
                    attribute_value=AttributeValueModel.objects.get(pk=value,deleted=0)

                    if attribute_value!=None:
                        productwtpsize.attribute_value=attribute_value
                    else:
                        return GraphQLError(send_err_res.raiseError("Attribute", "NV"))

                if key == 'product_id':
                    product = ProductModel.objects.get(pk=value, deleted=0)
                    if product!=None:
                        productwtpsize.product = product
                    else:
                        return GraphQLError(send_err_res.raiseError("Product", "NV"))
                else:
                    productwtpsize.__dict__[key] = value

                productwtpsize.created_at = timezone.now()
                productwtpsize.updated_at = timezone.now()
                productwtpsize.updated_by = product.user_id.appusers_id
                productwtpsize.deleted = 0
                product_wt_p_size_list.append(productwtpsize)

        try:
            for product_wt_p_size in product_wt_p_size_list:
                product_wt_p_size.save()
            return CreateProductWtpSize(productwtpsize=productwtpsize)
        except:
            raise
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateProductWtpSize(graphene.relay.ClientIDMutation):
    productwtpsize = graphene.Field(ProductWtpSizeType)

    class Input:
        data = graphene.List(ProductWtpSizeInput, required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        product_wt_p_size_list = []
        for d in data:
            if 'productwtpsize_id' in d:
                productwtpsize_update = ProductWtpSizeModel.objects.filter(
                    productwtpsize_id=d.productwtpsize_id).first()

                for key, value in d.items():

                    if key == 'attribute_value_id':
                        attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)

                        if attribute_value != None:
                            productwtpsize_update.attribute_value = attribute_value
                        else:
                            return GraphQLError(send_err_res.raiseError("Attribute", "NV"))

                    if key == 'product_id':
                        product = ProductModel.objects.get(pk=value, deleted=0)
                        productwtpsize_update.product=product
                        productwtpsize_update.updated_by = product.user_id.appusers_id

                    setattr(productwtpsize_update, key, value)
                    productwtpsize_update.updated_at = timezone.now()
                    product_wt_p_size_list.append(productwtpsize_update)
            else:
                productwtpsize_update = ProductWtpSizeModel()
                for key, value in d.items():
                    if key == 'size_weight':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == 'attribute_value_id':
                        attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)

                        if attribute_value != None:
                            productwtpsize_update.attribute_value = attribute_value
                        else:
                            return GraphQLError(send_err_res.raiseError("Attribute", "NV"))

                    if key == 'product_id':
                        product = ProductModel.objects.get(pk=value, deleted=0)
                        if product!=None:
                            productwtpsize_update.product = product
                            productwtpsize_update.updated_by = product.user_id.appusers_id
                        else:
                            return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    else:
                        productwtpsize_update.__dict__[key] = value


                productwtpsize_update.updated_at = timezone.now()

                productwtpsize_update.deleted = 0
                product_wt_p_size_list.append(productwtpsize_update)

        try:
            for product_wt_p_size in product_wt_p_size_list:
                product_wt_p_size.save()
            return UpdateProductWtpSize(productwtpsize=productwtpsize_update)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteProductWtpSize(graphene.relay.ClientIDMutation):
    """This mutation is to delete material composition in the database."""
    productwtpsize_id = graphene.Int()

    class Input:
        productwtpsize_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, productwtpsize_id):
        delete_productwtpsize = ProductWtpSizeModel.objects.filter(
            productwtpsize_id=productwtpsize_id).first()

        if delete_productwtpsize==None:
            return GraphQLError(send_err_res.raiseError("Product weight/Size", "NV"))

        delete_productwtpsize.deleted = 1

        try:
            delete_productwtpsize.save()
            return DeleteProductWtpSize(productwtpsize_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_product_wt_p_size = CreateProductWtpSize.Field()
    update_product_wt_p_size = UpdateProductWtpSize.Field()
    delete_product_wt_p_size = DeleteProductWtpSize.Field()
