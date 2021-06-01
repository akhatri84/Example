from django.utils import timezone

import graphene
from graphene import relay, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from ErrorHandler import send_err_res

from .models import MaterialCompositionModel
from product.models import ProductModel

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return MaterialCompositionModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length



class MaterialCompositionInput(graphene.InputObjectType):
    materialcomposition_id = graphene.Int()
    product_id = graphene.Int()
    material_name = graphene.String()
    percentage = graphene.String()


class MaterialCompositionType(DjangoObjectType):
    class Meta:
        model = MaterialCompositionModel
        filter_fields = {
            'material_name': ['exact','icontains', 'istartswith','contains'],
            'percentage': ['exact','icontains', 'istartswith','contains'],
            'deleted': ['exact'],
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

class Query(graphene.ObjectType):
    materialcomposition = relay.Node.Field(MaterialCompositionType)
    all_materialcomposition = DjangoFilterConnectionField(MaterialCompositionType, materialcomposition_pk=graphene.Int(),product_id=graphene.Int(),search=graphene.String(),
                                                orderBy=graphene.List(of_type=graphene.String))

    def resolve_all_materialcomposition(self, info, materialcomposition_pk=None,product_id=None, search=None, **kwargs):
        orderBy = kwargs.get('orderBy', None)

        materialcomposition_search = MaterialCompositionModel.objects.all()

        if materialcomposition_pk:
            materialcomposition_search = materialcomposition_search.filter(pk=materialcomposition_pk)
        if product_id:
            materialcomposition_search = materialcomposition_search.filter(product_id=product_id)
        if orderBy:
            materialcomposition_search = materialcomposition_search.order_by(*orderBy)
        if search:
            materialcomposition_search = materialcomposition_search.filter(
                Q(material_name__icontains=search) |
                Q(percentage__icontains=search) 
            )
        return materialcomposition_search


class CreateMaterialComposition(graphene.relay.ClientIDMutation):
    materialcomposition = graphene.Field(MaterialCompositionType)

    class Input:
        data = graphene.List(MaterialCompositionInput, required=True)

    # @login_required   
    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        material_composition_list = []
        for d in data:
            materialcomposition = MaterialCompositionModel()
            for key, value in d.items():
                if key == 'material_name' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))
                if key == 'product_id':
                    try:
                        product = ProductModel.objects.get(pk=value, deleted=0)
                    except:
                        product = None
                if key == 'percentage' and len(value.strip()) == 0:
                    raise GraphQLError(send_err_res.raiseError(key, "NP"))

                if key != 'product_id':
                    materialcomposition.__dict__[key] = value
                else:
                    if product == None:
                        return GraphQLError(send_err_res.raiseError("Product", "NV"))
                    materialcomposition.product_id = product      

                materialcomposition.created_at = timezone.now()
                materialcomposition.updated_at = timezone.now()
                materialcomposition.updated_by = product.user_id.appusers_id
                materialcomposition.deleted = 0
                material_composition_list.append(materialcomposition)

        try:
            for material in material_composition_list:
                material.save()
            return CreateMaterialComposition(materialcomposition=materialcomposition)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass
       

class UpdateMaterialComposition(graphene.relay.ClientIDMutation):
    materialcomposition = graphene.Field(MaterialCompositionType)

    class Input:
        data = graphene.List(MaterialCompositionInput, required=True)

    # @login_required   
    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        material_composition_list = []
        for d in data:
            if 'materialcomposition_id' in d:
                materialcomposition_update = MaterialCompositionModel.objects.filter(materialcomposition_id=d.materialcomposition_id).first()

                for key, value in d.items():
                    if key == 'material_name':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    
                    if key == 'product_id':
                        value = ProductModel.objects.get(pk=value, deleted=0)
                        materialcomposition_update.updated_by = value.user_id.appusers_id
                    
                    if key == 'percentage':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                   
                    setattr(materialcomposition_update, key, value)
                    materialcomposition_update.updated_at = timezone.now()
                    material_composition_list.append(materialcomposition_update)
            else:
                materialcomposition_update = MaterialCompositionModel()
                for key, value in d.items():
                    if key == 'material_name':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    elif key == 'product_id':
                        try:
                            product = ProductModel.objects.get(pk=value, deleted=0)
                        except:
                            product = None
                    elif key == 'percentage':
                        if len(value.strip()) == 0:
                            raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    if key != 'product_id':
                        materialcomposition_update.__dict__[key] = value
                    else:
                        if product == None:
                            return GraphQLError(send_err_res.raiseError("Product", "NV"))
                        materialcomposition_update.product_id = product 
                   
                materialcomposition_update.updated_at = timezone.now()
                materialcomposition_update.updated_by = product.user_id.appusers_id
                materialcomposition_update.deleted = 0
                material_composition_list.append(materialcomposition_update)

        try:
            for material in material_composition_list:
                material.save()
            return UpdateMaterialComposition(materialcomposition=materialcomposition_update)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteMaterialComposition(graphene.relay.ClientIDMutation):
    """This mutation is to delete material composition in the database."""
    materialcomposition_id = graphene.Int()

    class Input:
        materialcomposition_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, materialcomposition_id):
        delete_materialcomposition = MaterialCompositionModel.objects.filter(materialcomposition_id=materialcomposition_id).first()
        delete_materialcomposition.deleted = 1

        try:
            delete_materialcomposition.save()
            return DeleteMaterialComposition(materialcomposition_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass           
        
class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_material_composition = CreateMaterialComposition.Field()
    update_material_composition = UpdateMaterialComposition.Field()
    delete_material_composition = DeleteMaterialComposition.Field()







