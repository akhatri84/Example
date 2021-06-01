import graphene
from django.utils import timezone
from graphene import relay, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ErrorHandler import send_err_res
from impactsize.models import ImpactSizeModel
from product.models import ProductModel, AttributeValueModel


class ImpactSizeConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ImpactSizeModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ImpactSizeInput(graphene.InputObjectType):
    impactsize_id = graphene.Int()
    product_id = graphene.Int()
    attribute_value_id = graphene.Int()
    weight = graphene.String()
    kgco2 = graphene.String()
    liter = graphene.String()
    kmtravel = graphene.String()


class ImpactSizeType(DjangoObjectType):
    class Meta:
        model = ImpactSizeModel
        filter_fields = {
            'weight': ['exact'],
            'kgco2': ['exact'],
            'liter': ['exact'],
            'kmtravel': ['exact'],
            'deleted': ['exact'],
        }
        interfaces = (relay.Node,)
        connection_class = ImpactSizeConnection


class Query(graphene.ObjectType):
    impact_size = relay.Node.Field(ImpactSizeType)
    all_impact_size = DjangoFilterConnectionField(ImpactSizeType, product_id=graphene.Int(),
                                                  attribute_value_id=graphene.Int())

    def resolve_all_impact_size(self, info, product_id=None, attribute_value_id=None, **kwargs):
        impact_size = ImpactSizeModel.objects.all()

        if product_id:
            impact_size = impact_size.filter(product_id=product_id)

        if attribute_value_id:
            impact_size = impact_size.filter(attribute_value_id=attribute_value_id)

        return impact_size


class CreateImpactSize(graphene.relay.ClientIDMutation):
    impactsize = graphene.Field(ImpactSizeType)

    class Input:
        data = graphene.List(ImpactSizeInput, required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        impact_size_list = []
        upd_prd_list = []
        app_id = 1
        for d in data:
            impactsize = ImpactSizeModel()
            for key, value in d.items():

                if key == 'product_id':
                    product = ProductModel.objects.get(pk=value, deleted=0)
                    if product != None:
                        impactsize.product = product
                        app_id = product.user_id.appusers_id
                    else:
                        return GraphQLError(send_err_res.raiseError("Product", "NV"))
                elif key == "attribute_value_id":
                    attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)
                    if attribute_value.value == "M":
                        upd_prd_list.append(True)
                    else:
                        upd_prd_list.append(False)

                    if attribute_value != None:
                        impactsize.attribute_value = attribute_value
                    else:
                        return GraphQLError(send_err_res.raiseError("Attribute Value", "NV"))
                else:
                    impactsize.__dict__[key] = value

            impactsize.created_at = timezone.now()
            impactsize.updated_at = timezone.now()
            impactsize.updated_by = app_id
            impactsize.deleted = 0
            impact_size_list.append(impactsize)

        try:
            i = 0
            for impact_size in impact_size_list:
                impact_size.save()
                if upd_prd_list[i]:
                    ProductModel.objects.filter(pk=impact_size.product_id).update(kgco2=impact_size.kgco2,
                                                                                  liter=impact_size.liter,
                                                                                  kmtravel=impact_size.kmtravel)
                i = i + 1
            return CreateImpactSize(impactsize=impactsize)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateImpactSize(graphene.relay.ClientIDMutation):
    impactsize = graphene.Field(ImpactSizeType)

    class Input:
        data = graphene.List(ImpactSizeInput, required=True)

    # @login_required   
    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        impact_size_list = []
        for d in data:
            if 'impactsize_id' in d:
                impactsize_update = ImpactSizeModel.objects.filter(product_id=d["product_id"],
                                                                   impactsize_id=d.impactsize_id, deleted=0).first()

                for key, value in d.items():
                    if key == 'product_id':
                        product = ProductModel.objects.get(pk=value, deleted=0)
                        if product != None:
                            impactsize_update.product = product
                            impactsize_update.updated_by = product.user_id.appusers_id
                        else:
                            return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    elif key == "attribute_value_id":
                        attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)

                        if attribute_value != None:
                            impactsize_update.attribute_value = attribute_value
                        else:
                            return GraphQLError(send_err_res.raiseError("Attribute Value", "NV"))
                    else:
                        setattr(impactsize_update, key, value)
                    impactsize_update.updated_at = timezone.now()
                    impact_size_list.append(impactsize_update)
            else:
                impactsize_update = ImpactSizeModel()
                for key, value in d.items():
                    if key == 'product_id':
                        product = ProductModel.objects.get(pk=value, deleted=0)
                        if product != None:
                            impactsize_update.product = product
                            impactsize_update.updated_by = product.user_id.appusers_id
                        else:
                            return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    elif key == "attribute_value_id":
                        attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)

                        if attribute_value != None:
                            impactsize_update.attribute_value = attribute_value
                        else:
                            return GraphQLError(send_err_res.raiseError("Attribute Value", "NV"))
                    else:
                        impactsize_update.__dict__[key] = value

                impactsize_update.updated_at = timezone.now()

                impactsize_update.deleted = 0
                impact_size_list.append(impactsize_update)

        try:

            new_product_id = 0
            for impact_size in impact_size_list:
                new_product_id = impact_size.product_id
                impact_size.save()

            impact_size = ImpactSizeModel.objects.filter(product_id=new_product_id,
                                                         attribute_value__value="M", deleted=0).first()

            if impact_size == None:
                impact_size = ImpactSizeModel.objects.filter(product_id=new_product_id, deleted=0).first()
                ProductModel.objects.filter(pk=impact_size.product_id,
                                            deleted=0).update(
                    kgco2=impact_size.kgco2.replace(",","."),
                    liter=impact_size.liter.replace(",","."),
                    kmtravel=impact_size.kmtravel.replace(",","."))
            else:
                ProductModel.objects.filter(pk=impact_size.product_id,
                                            deleted=0).update(
                    kgco2=impact_size.kgco2,
                    liter=impact_size.liter,
                    kmtravel=impact_size.kmtravel)

            return UpdateImpactSize(impactsize=impactsize_update)
        except:
            raise
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteImpactSize(graphene.relay.ClientIDMutation):
    """This mutation is to delete material composition in the database."""
    impactsize_id = graphene.Int()

    class Input:
        impactsize_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, impactsize_id):
        delete_impactsize = ImpactSizeModel.objects.filter(
            impactsize_id=impactsize_id).first()

        if delete_impactsize == None:
            return GraphQLError(send_err_res.raiseError("impact size", "NV"))

        delete_impactsize.deleted = 1

        try:
            delete_impactsize.save()
            return DeleteImpactSize(impactsize_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_impact_size = CreateImpactSize.Field()
    update_impact_size = UpdateImpactSize.Field()
    delete_impact_size = DeleteImpactSize.Field()
