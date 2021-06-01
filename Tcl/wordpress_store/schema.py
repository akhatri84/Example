import sys
from django.utils import timezone

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

class WordpressProductTypes(DjangoObjectType):
    class Meta:
        model = ProductModel
        fields = '__all__'

class CreateWordpressProducts(graphene.Mutation):
    product = graphene.List(WordpressProductTypes)
    class Arguments:      
        user_id = graphene.Int()
    
    def mutate(self, info, user_id):
        app_config = ApiConfigModel.objects.filter(user_id=user_id).filter(deleted=0).first()

        platform = app_config.platform

        if app_config == None:
            return GraphQLError(send_err_res.raiseDBError("API_CONFIG_NOT_FOUND"))

        productlist = []

        if platform.upper() == 'WORDPRESS':
            wcapi = API(
                url=app_config.apiend_point,
                consumer_key=app_config.api_key,
                consumer_secret=app_config.secret_key                        
            )

            data = wcapi.get("products").json()
     
            if len(data) == 0:
                return GraphQLError("No Data found")              
            else:
                # Loop through each products in fetched list
                for i in range(len(data)):
                    # search for product in database             
                    upd_product = ProductModel.objects.filter(shopify_product_id=str(data[i]["id"]),deleted=0).first()
                    # if Product not found create new product
                    if upd_product == None:
                        product = ProductModel()
                        user = AppUserModel.objects.get(pk=user_id)
                        product.user_id = user
                        product.shopify_product_id = data[i]["id"]
                        product.product_name = data[i]["name"]
                        # remove HTML tags from body_html variable
                        prd_desc = re.compile('<.*?>')
                        prd_desc = re.sub(prd_desc, '', data[i]["short_description"])
                        product.short_description = prd_desc                 
                        product.product_type = data[i]["type"]
                        product.product_weight = data[i]["weight"]
                        product.product_link = data[i]["permalink"]
                        product.price = int(float(data[i]["price"]))
                        product.platform = app_config.platform
                        if data[i]["status"] == "publish":
                            product.status = True
                        product.created_at = timezone.now()
                        product.updated_at = timezone.now()
                        product.updated_by = user.appusers_id
                        product.deleted = 0
                        productlist.append(product)
                        try:
                            product.save()
                        except:
                            raise GraphQLError(send_err_res.raiseDBError("SW"))                  
                    else:
                        # if product found then update it
                        user = AppUserModel.objects.get(pk=user_id)
                        upd_product.user_id = user
                        upd_product.product_name =  data[i]["name"]
                        # remove HTML tags from body_html variable
                        prd_desc = re.compile('<.*?>')
                        prd_desc = re.sub(prd_desc, '', data[i]["short_description"])
                        upd_product.short_description = prd_desc
                        upd_product.product_type = data[i]["type"]
                        upd_product.product_weight =  data[i]["weight"]    
                        upd_product.price = int(float(data[i]["price"]))
                        upd_product.product_link = data[i]["permalink"] 
                        if data[i]["status"] == "publish":
                            upd_product.status = True 
                        upd_product.updated_at = timezone.now()
                        upd_product.updated_by = user.appusers_id                 
                        try:
                            upd_product.save()
                        except:
                            raise GraphQLError(send_err_res.raiseDBError("SW"))              
                      
                    if len(data[i]["images"]) == 1: 
                        # Get the file name and file extention from URL
                        if upd_product == None:
                            product_files = ProductFilesModel()
                            product_files.product_id = product
                            product_files.created_by = user.appusers_id
                            product_files.created_at = timezone.now()
                        else:
                            product_files = ProductFilesModel.objects.filter(product_id=upd_product.product_id,deleted=0).first()
                            product_files.updated_by = user.appusers_id
                            product_files.updated_at = timezone.now()
                        imgsrc = data[i]["images"][0]['src']
                        product_files.aws_file_url = imgsrc
                        filename = imgsrc.split('/')[-1].split('?')[0]
                        file_extention = filename.split('.')[1]
                        product_files.file_extension = file_extention               
                        product_files.file_type = "pic"   
                        product_files.store_file_id = str(data[i]["images"][0]['id'])               
                        product_files.updated_at = timezone.now()                      
                        product_files.deleted = 0             
                        try:
                            product_files.save()
                        except:
                            return GraphQLError(send_err_res.raiseDBError("SW"))           
            products = productlist
            if len(productlist) == 0:
                return GraphQLError(send_err_res.raiseDBError("PAS"))

        return CreateWordpressProducts(product=products)

class Mutation(graphene.ObjectType):
    """Root mutation class."""
    create_wordpress_products = CreateWordpressProducts.Field()

