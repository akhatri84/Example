import socket
from datetime import datetime

import graphene
from decouple import config
from django.db.models import Q
from django.utils import timezone
from graphene import relay, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ErrorHandler import send_err_res
from app_user.models import AppUserModel
from email_notification import notify_client
from onboarding.models import OnboardingModel
from .models import ProductModel, AttributeModel, AttributeValueModel, ProductAttributeModel, ProductMonthClickCount
from .sub_schema import addattribute


class MonthCountConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ProductMonthClickCount.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class AttributeConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return Attribute.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class AttributeValueConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return AttributeValueModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ProductAttributeConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ProductAttributeModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    filter_count = graphene.Int()

    def resolve_total_count(self, info):
        return ProductModel.objects.all().count()

    def resolve_filter_count(self, info):
        return self.length


class MonthCountType(DjangoObjectType):
    class Meta:
        model = ProductMonthClickCount
        filter_fields = {'timestamp': ['exact'],
                         'day': ['exact'],
                         'month': ['exact'],
                         'year': ['exact'],
                         'product_id': ['exact'],
                         'deleted': ['exact'], }
        interfaces = (relay.Node,)
        connection_class = MonthCountConnection


class AttributeType(DjangoObjectType):
    class Meta:
        model = AttributeModel
        filter_fields = {'attribute_name': ['exact', 'icontains', 'istartswith', 'contains'], 'deleted': ['exact'], }
        interfaces = (relay.Node,)
        connection_class = AttributeConnection


class AttributeValueType(DjangoObjectType):
    class Meta:
        model = AttributeValueModel
        filter_fields = {'value': ['exact', 'icontains', 'istartswith', 'contains'],
                         'slug': ['exact', 'icontains', 'istartswith', 'contains'],
                         'deleted': ['exact'],
                         }
        interfaces = (relay.Node,)
        connection_class = AttributeValueConnection


class ProductAttributeType(DjangoObjectType):
    class Meta:
        model = ProductAttributeModel
        filter_fields = {'deleted': ['exact'], }
        interfaces = (relay.Node,)
        connection_class = ProductAttributeConnection


class ProductType(DjangoObjectType):
    class Meta:
        model = ProductModel
        filter_fields = {
            'product_name': ['exact', 'icontains', 'istartswith', 'contains'],
            'short_description': ['exact', 'icontains', 'istartswith', 'contains'],
            'detail_description': ['exact', 'icontains', 'istartswith', 'contains'],
            'price': ['exact', 'icontains', 'istartswith', 'contains'],
            'type_of_fashion_product': ['exact', 'icontains', 'istartswith', 'contains'],
            'product_accessories': ['exact', 'icontains', 'istartswith', 'contains'],
            'product_weight': ['exact', 'icontains', 'istartswith', 'contains'],
            'yearly_amount_of_items_procured': ['exact', 'icontains', 'istartswith', 'contains'],
            'average_lifetime_of_your_product': ['exact', 'icontains', 'istartswith', 'contains'],
            'end_of_life_biodegradable': ['exact', 'icontains', 'contains'],
            'end_of_life_recyclable': ['exact', 'icontains', 'contains'],
            'end_of_life_product_as_a_service': ['exact', 'icontains', 'contains'],
            'end_of_life_repair_service_brand': ['exact', 'icontains', 'contains'],
            'end_of_life_others': ['exact', 'icontains', 'istartswith', 'contains'],
            'link_to_brand': ['exact', 'icontains', 'istartswith', 'contains'],
            'gender': ['exact', 'icontains', 'istartswith', 'contains'],
            'transparency_score': ['exact', 'icontains', 'istartswith', 'contains'],
            'status': ['exact', 'icontains', 'istartswith', 'contains'],
            'click_count': ['exact'],
            'product_link': ['exact', 'icontains', 'istartswith', 'contains'],
            'platform': ['exact', 'icontains', 'istartswith', 'contains'],
            'biobased_material': ['exact'],
            'refurbished_material': ['exact'],
            'reused_material': ['exact'],
            'recycled_material': ['exact'],
            'vegan': ['exact'],
            'second_life_possible': ['exact'],
            'social_impact': ['exact', 'icontains', 'istartswith', 'contains'],
            'organic_fiber': ['exact'],
            'showon_landing_page': ['exact'],
            'kgco2': ['exact'],
            'liter': ['exact'],
            'kmtravel': ['exact'],
            'deleted': ['exact'],

        }
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    product = relay.Node.Field(ProductType)
    all_product = DjangoFilterConnectionField(ProductType, product_pk=graphene.Int(), user_id=graphene.Int(),
                                              userlist=graphene.List(of_type=graphene.Int),
                                              companylist=graphene.List(of_type=graphene.String),
                                              productlist=graphene.List(of_type=graphene.Int),
                                              slugfield=graphene.String(),
                                              sizelist=graphene.List(of_type=graphene.String),
                                              categorylist=graphene.List(of_type=graphene.String),
                                              colorlist=graphene.List(of_type=graphene.String),
                                              genderlist=graphene.List(of_type=graphene.String),
                                              search=graphene.String(),
                                              orderBy=graphene.List(of_type=graphene.String))

    attribute = relay.Node.Field(AttributeType)
    all_attribute = DjangoFilterConnectionField(AttributeType)

    attribute_value = relay.Node.Field(AttributeValueType)
    all_attribute_value = DjangoFilterConnectionField(AttributeValueType, attribute_id=graphene.Int())

    product_attribute = relay.Node.Field(ProductAttributeType)
    all_product_attribute = DjangoFilterConnectionField(ProductAttributeType)

    product_month_click = relay.Node.Field(MonthCountType)
    all_product_month_click = DjangoFilterConnectionField(MonthCountType)

    def resolve_all_product_month_click(self, info, product_id=None, **kwargs):
        month_click = ProductMonthClickCount.objects.all()

        if product_id:
            month_click = month_click.filter(product_id=product_id)
            return month_click

    def resolve_all_attribute(self, info, **kwargs):
        return AttributeModel.objects.all()

    def resolve_all_attribute_value(self, info, attribute_id=None, **kwargs):
        attribute_value = AttributeValueModel.objects.all()

        if attribute_id:
            attribute_value = attribute_value.filter(attribute__attribute_id=attribute_id)
        return attribute_value

    def resolve_all_product_attribute(self, info, **kwargs):
        return ProductAttributeModel.objects.all()

    def resolve_all_product(self, info, product_pk=None, user_id=None, userlist=None, companylist=None,
                            productlist=None, slugfield=None, sizelist=None, categorylist=None, colorlist=None,
                            genderlist=None,
                            search=None, **kwargs):

        orderBy = kwargs.get('orderBy', None)

        products = ProductModel.objects.all()
        if product_pk:
            products = products.filter(pk=product_pk)
        if user_id:
            products = products.filter(user_id=user_id)
        if userlist:
            products = products.filter(user_id__in=userlist)
        if companylist:
            userlist = []
            for company in companylist:
                onboard = OnboardingModel.objects.filter(company=company).first()
                product_count = products.filter(user_id=onboard.user_id).count()
                if product_count > 0:
                    userlist.append(onboard.user_id)
            products = products.filter(user_id__in=userlist)
        if productlist:
            products = products.filter(product_id__in=productlist)
        if slugfield:
            products = products.filter(slug=slugfield)
        if sizelist:
            products = products.filter(impactsizemodel__attribute_value__slug__in=sizelist,
                                       impactsizemodel__deleted=0).distinct()
        if categorylist:
            products = products.filter(productattributemodel__attribute_value__slug__in=categorylist).distinct()
        if genderlist:
            if "Male" in genderlist or "Female" in genderlist:
                genderlist.append("Unisex")
            products = products.filter(gender__in=genderlist)
        if orderBy:
            products = products.order_by(*orderBy).distinct()
        if search:
            products = products.filter(
                Q(product_name__icontains=search) |
                Q(short_description__icontains=search) |
                Q(detail_description__icontains=search) |
                Q(price__icontains=search) |
                Q(type_of_fashion_product__icontains=search) |
                Q(product_accessories__icontains=search) |
                Q(product_weight__icontains=search) |
                Q(yearly_amount_of_items_procured__icontains=search) |
                Q(average_lifetime_of_your_product__icontains=search) |
                Q(end_of_life_biodegradable__icontains=search) |
                Q(end_of_life_recyclable__icontains=search) |
                Q(end_of_life_product_as_a_service__icontains=search) |
                Q(end_of_life_repair_service_brand__icontains=search) |
                Q(end_of_life_others__icontains=search) |
                Q(link_to_brand__icontains=search) |
                Q(gender__icontains=search) |
                Q(transparency_score__icontains=search) |
                Q(status__icontains=search) |
                Q(social_impact__icontains=search) |
                Q(platform__icontains=search) |
                Q(product_link__icontains=search) |
                Q(colors__icontains=search)

            )
        return products


class Attribute(graphene.relay.ClientIDMutation):
    new_attribute = graphene.Field(AttributeType)

    class Input:
        attribute_id = graphene.Int()
        attribute_name = graphene.String(required=True)
        user_id = graphene.Int()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        if "attribute_id" in kwargs:
            new_attribute = AttributeModel.objects.get(pk=kwargs["attribute_id"], deleted=0)
        else:
            new_attribute = AttributeModel()

        for key, value in kwargs.items():
            if key == "attribute_name" and len(kwargs["attribute_name"]) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    raise GraphQLError(send_err_res.raiseDBError("User is not present"))

            new_attribute.__dict__[key] = value

        new_attribute.created_at = timezone.now()
        new_attribute.updated_at = timezone.now()
        new_attribute.updated_by = app_user.appusers_id
        new_attribute.deleted = 0

        try:
            new_attribute.save()
            return Attribute(new_attribute=new_attribute)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class AttributeValue(graphene.relay.ClientIDMutation):
    attributeValue = graphene.Field(AttributeValueType)

    class Input:
        attribute_value_id = graphene.Int()
        attribute_id = graphene.Int(required=True)
        value = graphene.String(required=True)
        user_id = graphene.Int()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        if "attribute_value_id" in kwargs:
            attributeValue = AttributeValueModel.objects.get(pk=kwargs["attribute_value_id"], deleted=0)
        else:
            attributeValue = AttributeValueModel()

        for key, value in kwargs.items():
            if key == "value" and len(kwargs["value"]) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key == "attribute_id":
                atribute = AttributeModel.objects.get(pk=value, deleted=0)
                if atribute != None:
                    attributeValue.attribute = atribute
                else:
                    raise GraphQLError(send_err_res.raiseDBError("Attribute is not Valid"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    raise GraphQLError(send_err_res.raiseDBError("User is not present"))

            attributeValue.__dict__[key] = value

        attributeValue.created_at = timezone.now()
        attributeValue.updated_at = timezone.now()
        attributeValue.updated_by = app_user.appusers_id
        attributeValue.deleted = 0

        try:
            attributeValue.save()
            return AttributeValue(attributeValue=attributeValue)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class ProductAttribute(graphene.relay.ClientIDMutation):
    productAttribute = graphene.Field(ProductAttributeType)

    class Input:
        product_attribute_id = graphene.Int()
        attribute_value_id = graphene.Int()
        product_id = graphene.Int()
        user_id = graphene.Int()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        if "product_attribute_id" in kwargs:
            productAttribute = ProductAttributeModel.objects.get(pk=kwargs["product_attribute_id"], deleted=0)
        else:
            productAttribute = ProductAttributeModel()

        for key, value in kwargs.items():
            if key == "attribute_value_id":
                try:
                    attribute_value = AttributeValueModel.objects.get(pk=value, deleted=0)
                    productAttribute.attribute_value = attribute_value
                except:
                    raise GraphQLError(send_err_res.raiseDBError("Attribute value is not Valid"))
            elif key == "product_id":
                try:
                    product = ProductModel.objects.get(pk=value, deleted=0)
                    productAttribute.product = product
                except:
                    raise GraphQLError(send_err_res.raiseDBError("Product not available"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    raise GraphQLError(send_err_res.raiseDBError("User is not present"))

            productAttribute.__dict__[key] = value

        productAttribute.created_at = timezone.now()
        productAttribute.updated_at = timezone.now()
        productAttribute.updated_by = app_user.appusers_id
        productAttribute.deleted = 0

        try:
            productAttribute.save()
            return ProductAttribute(productAttribute=productAttribute)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class CreateProduct(graphene.relay.ClientIDMutation):
    product = graphene.Field(ProductType)

    class Input:
        user_id = graphene.Int()
        supply_chain_id = graphene.Int(required=False)
        product_name = graphene.String()
        short_description = graphene.String()
        detail_description = graphene.String()
        type_of_fashion_product = graphene.String()
        product_accessories = graphene.String()
        product_weight = graphene.String()
        yearly_amount_of_items_procured = graphene.String()
        average_lifetime_of_your_product = graphene.String()
        end_of_life_biodegradable = graphene.Boolean()
        end_of_life_recyclable = graphene.Boolean()
        end_of_life_product_as_a_service = graphene.Boolean()
        end_of_life_repair_service_brand = graphene.Boolean()
        end_of_life_others = graphene.String()
        link_to_brand = graphene.String()
        gender = graphene.String()
        transparency_score = graphene.String()
        status = graphene.Boolean()
        price = graphene.String()
        click_count = graphene.Int()
        product_link = graphene.String()
        biobased_material = graphene.Boolean()
        refurbished_material = graphene.Boolean()
        reused_material = graphene.Boolean()
        recycled_material = graphene.Boolean()
        vegan = graphene.Boolean()
        second_life_possible = graphene.Boolean()
        social_impact = graphene.String()
        organic_fiber = graphene.Boolean()
        showon_landing_page = graphene.Boolean()
        colors = graphene.String()
        sizes = graphene.List(graphene.String)
        product_type = graphene.List(graphene.String)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        product = ProductModel()

        for key, value in kwargs.items():
            if key == 'product_name' and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == 'user_id':
                try:
                    app_user = AppUserModel.objects.get(pk=value, deleted=0)
                except:
                    app_user = None
            if key == "short_description" and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == "product_weight" and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))
            if key == "yearly_amount_of_items_procured" and len(value.strip()) == 0:
                raise GraphQLError(send_err_res.raiseError(key, "NP"))

            if key != 'user_id':
                product.__dict__[key] = value
            else:
                if app_user == None:
                    return GraphQLError(send_err_res.raiseError("User", "NV"))
                product.user_id = app_user

        product.created_at = timezone.now()
        product.updated_at = timezone.now()
        product.updated_by = app_user.appusers_id
        product.deleted = 0

        try:
            product.save()

            addattribute(kwargs, "sizes", product.product_id, 1)
            addattribute(kwargs, "product_type", product.product_id, 1)
            # addattribute(kwargs, "colors",  product.product_id,1)

            context = {
                "Product Name": product.product_name,
                "Brand Name": product.link_to_brand
            }
            notify_client.sendMailApp(
                config("ADMIN_EMAIL"), "Product", "Add", context)
            return CreateProduct(product=product)
        except:
            raise
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateProduct(graphene.relay.ClientIDMutation):
    product = graphene.Field(ProductType)

    class Input:
        product_id = graphene.Int(required=True)
        supply_chain_id = graphene.Int(required=False)
        user_id = graphene.Int(required=True)
        product_name = graphene.String()
        short_description = graphene.String()
        detail_description = graphene.String()
        type_of_fashion_product = graphene.String()
        product_accessories = graphene.String()
        product_weight = graphene.String()
        yearly_amount_of_items_procured = graphene.String()
        average_lifetime_of_your_product = graphene.String()
        end_of_life_biodegradable = graphene.Boolean()
        end_of_life_recyclable = graphene.Boolean()
        end_of_life_product_as_a_service = graphene.Boolean()
        end_of_life_repair_service_brand = graphene.Boolean()
        end_of_life_others = graphene.String()
        link_to_brand = graphene.String()
        gender = graphene.String()
        transparency_score = graphene.String()
        status = graphene.Boolean()
        price = graphene.String()
        click_count = graphene.Int()
        product_link = graphene.String()
        biobased_material = graphene.Boolean()
        refurbished_material = graphene.Boolean()
        reused_material = graphene.Boolean()
        recycled_material = graphene.Boolean()
        vegan = graphene.Boolean()
        second_life_possible = graphene.Boolean()
        social_impact = graphene.String()
        organic_fiber = graphene.Boolean()
        showon_landing_page = graphene.Boolean()
        colors = graphene.String()
        sizes = graphene.List(graphene.String)
        product_type = graphene.List(graphene.String)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, product_id, **kwargs):
        product_update = ProductModel.objects.filter(
            product_id=product_id, deleted=0).first()

        try:
            if product_update != None:
                for key, value in kwargs.items():
                    if key == 'product_name' and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == "short_description" and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == "product_weight" and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))
                    if key == "yearly_amount_of_items_procured" and len(value.strip()) == 0:
                        raise GraphQLError(send_err_res.raiseError(key, "NP"))

                    if key == 'user_id':
                        try:
                            app_user = AppUserModel.objects.get(
                                pk=value, deleted=0)
                        except:
                            app_user = None

                    if key != 'user_id':
                        setattr(product_update, key, value)
                    else:
                        if app_user == None:
                            return GraphQLError(send_err_res.raiseError("User", "NV"))
                        product_update.user_id = app_user

                product_update.updated_at = timezone.now()
                product_update.updated_by = app_user.appusers_id

                product_update.save()
                addattribute(kwargs, "sizes", product_id, 0)
                addattribute(kwargs, "product_type", product_id, 0)
                # addattribute(kwargs, "colors",  product_id,0)

                context = {
                    "Product Name": product_update.product_name,
                    "Brand Name": product_update.link_to_brand
                }
                notify_client.sendMailApp(
                    config("ADMIN_EMAIL"), "Product", "Update", context)
                return UpdateProduct(product=product_update)
            else:
                return GraphQLError(send_err_res.raiseDBError("NR"))
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class DeleteAttribute(graphene.relay.ClientIDMutation):
    attribute_id = graphene.Int()

    class Input:
        attribute_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, attribute_id):
        delete_attribute = AttributeModel.objects.filter(attribute_id=attribute_id).first()

        if delete_attribute == None:
            raise GraphQLError(send_err_res.raiseDBError("NR"))
        delete_attribute.deleted = 1

        try:
            delete_attribute.save()
            return DeleteAttribute(attribute_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))


class DeleteAttributeValue(graphene.relay.ClientIDMutation):
    attribute_value_id = graphene.Int()

    class Input:
        attribute_value_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, attribute_value_id):
        deleted_attribute_value = AttributeValueModel.objects.filter(attribute_value_id=attribute_value_id).first()

        if deleted_attribute_value == None:
            raise GraphQLError(send_err_res.raiseDBError("NR"))
        deleted_attribute_value.deleted = 1

        try:
            deleted_attribute_value.save()
            return DeleteAttributeValue(attribute_value_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))


class DeleteProductAttribute(graphene.relay.ClientIDMutation):
    product_attribute_id = graphene.Int()

    class Input:
        product_attribute_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, product_attribute_id):
        deleted_product_attribute = ProductAttributeModel.objects.filter(
            product_attribute_id=product_attribute_id).first()

        if deleted_product_attribute == None:
            raise GraphQLError(send_err_res.raiseDBError("NR"))
        deleted_product_attribute.deleted = 1

        try:
            deleted_product_attribute.save()
            return DeleteProductAttribute(product_attribute_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))


class DeleteProduct(graphene.relay.ClientIDMutation):
    product_id = graphene.Int()

    class Input:
        product_id = graphene.Int(required=True)

    # @login_required
    @classmethod
    def mutate_and_get_payload(cls, root, info, product_id):
        delete_product = ProductModel.objects.filter(
            product_id=product_id).first()
        delete_product.deleted = 1

        try:
            context = {
                "Product Name": delete_product.product_name,
                "Brand Name": delete_product.link_to_brand
            }
            delete_product.save()
            notify_client.sendMailApp(
                config("ADMIN_EMAIL"), "Product", "Delete", context)
            return DeleteProduct(product_id)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class UpdateProductClick(graphene.relay.ClientIDMutation):
    product = graphene.Field(ProductType)
    product_month = graphene.Field(MonthCountType)

    class Input:
        product_id = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, product_id):

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        update_product = ProductModel.objects.filter(product_id=product_id).first()

        update_product.click_count = update_product.click_count + 1

        product_month = ProductMonthClickCount()

        product_month.product_id = update_product

        product_month.day = datetime.now().day
        product_month.month = datetime.now().month
        product_month.year = datetime.now().year
        product_month.ip_address = ip_address

        clickcnt = ProductMonthClickCount.objects.filter(product_id=product_id, day=datetime.now().day,
                                                         month=datetime.now().month, year=datetime.now().year).count()
        try:
            if clickcnt < 5:
                update_product.save()
                product_month.save()
            return UpdateProductClick(product=update_product, product_month=product_month)
        except:
            return GraphQLError(send_err_res.raiseDBError("SW"))
        finally:
            pass


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    attribute = Attribute.Field()
    delete_attribute = DeleteAttribute.Field()
    attribute_value = AttributeValue.Field()
    delete_attribute_value = DeleteAttributeValue.Field()
    product_attribute = ProductAttribute.Field()
    delete_product_attribute = DeleteProductAttribute.Field()
    update_product_click = UpdateProductClick.Field()
