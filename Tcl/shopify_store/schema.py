import sys

sys.path.append('../')

import graphene
from graphene_django import DjangoObjectType

from graphql import GraphQLError

from ErrorHandler import send_err_res
from product_files.models import ProductFilesModel
import re
from product.models import ProductModel
from api_config.models import ApiConfigModel
from app_user.models import AppUserModel
import requests
from woocommerce import API


def update_product_files(product_files, productfiles_src, productfiles_id):
    product_files.store_file_id = productfiles_id

    filename = productfiles_src.split('/')[-1].split('?')[0]
    file_extention = filename.split('.')[1]

    product_files.file_extension = file_extention

    product_files.aws_file_url = productfiles_src
    product_files.file_extension = file_extention
    product_files.file_type = "pic"
    try:
        product_files.save()
    except:
        return GraphQLError(send_err_res.raiseDBError("SW"))


def update_product_variants(product_files,variants_list):
    inv_qty_list = []
    weight_list = []
    color_list = []

    if len(variants_list) > 0:
        for i in range(len(variants_list)):
            if str(variants_list[i]["inventory_quantity"]):
                inv_qty_list.append(str(variants_list[i]["inventory_quantity"]))
            if str(variants_list[i]["weight"]):
                weight_list.append(str(variants_list[i]["weight"]))
            if variants_list[i]["option2"]:
                color_list.append(variants_list[i]["option2"])

        if len(inv_qty_list) > 0:
            product_files.yearly_amount_of_items_procured = ','.join(inv_qty_list)

        if len(weight_list) > 0:
            product_files.product_weight = ','.join(weight_list)

        if len(color_list) > 0:
            product_files.colors = ','.join(color_list)


class ProductTypes(DjangoObjectType):
    class Meta:
        model = ProductModel
        fields = '__all__'


class CreateProducts(graphene.Mutation):
    class Arguments:
        platform = graphene.String()
        user_id = graphene.Int()

    product = graphene.List(ProductTypes)

    def mutate(self, info,platform, user_id):

        app_config = \
            ApiConfigModel.objects.filter(user_id=user_id).filter(deleted=0).first()


        if app_config == None:
            return GraphQLError(send_err_res.raiseDBError("API_CONFIG_NOT_FOUND"))

        url_src = "https://" + app_config.api_key + ":" + app_config.secret_key + "@" + app_config.apiend_point
        url = requests.get(url_src)


        if url.status_code != 200:
            return GraphQLError(send_err_res.raiseDBError("NE"))

        data = url.json()
        if len(data['products']) == 0:
            return GraphQLError("No Data found")

        productlist = []

        # Loop through each products in fetched list
        for i in range(len(data['products'])):

            # search for product in database
            product = ProductModel()
            upd_product = ProductModel.objects.filter(shopify_product_id=str(data['products'][i]["id"]),
                                                      deleted=0).first()

            # if Product not found create new product
            if upd_product == None:
                user = AppUserModel.objects.get(pk=user_id)
                product.user_id = user

                update_product_variants(product, data['products'][i]["variants"])

                product.shopify_product_id = data['products'][i]["id"]
                product.product_name = data['products'][i]["title"]

                # remove HTML tags from body_html variable
                prd_desc = re.compile('<.*?>')
                prd_desc = re.sub(prd_desc, '', data['products'][i]["body_html"])
                product.short_description = prd_desc

                product.link_to_brand = data['products'][i]["vendor"]
                product.product_type = data['products'][i]["product_type"]
                product.gender = data['products'][i]["tags"]
                product.price = int(float(data['products'][i]["variants"][0]["price"]))
                product.platform = app_config.platform
            else:
                # if product found then update it
                user = AppUserModel.objects.get(pk=user_id)
                product.user_id = user

                update_product_variants(upd_product, data['products'][i]["variants"])

                upd_product.product_name = data['products'][i]["title"]

                # remove HTML tags from body_html variable
                prd_desc = re.compile('<.*?>')
                prd_desc = re.sub(prd_desc, '', data['products'][i]["body_html"])
                upd_product.short_description = prd_desc

                upd_product.link_to_brand = data['products'][i]["vendor"]
                upd_product.product_type = data['products'][i]["product_type"]
                upd_product.gender = data['products'][i]["tags"]
                upd_product.price = int(float(data['products'][i]["variants"][0]["price"]))

            try:
                # add product to the database if not found else update.
                if upd_product == None:
                    product.save()

            except:
                return GraphQLError(send_err_res.raiseDBError("SW"))

            if upd_product == None:
                productlist.append(product.product_id)
                if len(data['products'][i]["images"]) > 0:
                    for j in range(len(data['products'][i]["images"])):
                        product_files = ProductFilesModel()
                        product_files.product_id = product
                        update_product_files(product_files, data['products'][i]["images"][j]["src"], data['products'][i]["images"][j]["id"])

            else:
                if len(data['products'][i]["images"]) > 0:

                    for j in range(len(data['products'][i]["images"])):
                        product_files = ProductFilesModel.objects.filter(product_id=upd_product.product_id).filter(
                            store_file_id=data['products'][i]["images"][j]["id"]).filter(deleted=0).first()

                        if product_files == None:
                            product_files = ProductFilesModel()

                        product_files.product_id = upd_product
                        update_product_files(product_files, data['products'][i]["images"][j]["src"],
                                             data['products'][i]["images"][j]["id"])

                        try:
                            product_files.save()
                        except:
                            return GraphQLError(send_err_res.raiseDBError("SW"))


        products = ProductModel.objects.filter(product_id__in=productlist).filter(deleted=0).all()

        # if len(productlist) == 0:
        #     return GraphQLError(send_err_res.raiseDBError("PAS"))

        return CreateProducts(product=products)


class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_products = CreateProducts.Field()
