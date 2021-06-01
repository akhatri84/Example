from django.shortcuts import HttpResponse
from product.models import ProductModel
from product_files.models import ProductFilesModel
from api_config.models import ApiConfigModel
from app_user.models import AppUserModel
from ErrorHandler import send_err_res

import json

import re
from django.views.decorators.csrf import csrf_exempt


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
        return HttpResponse(send_err_res.raiseDBError("SW"))


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


@csrf_exempt
def createProduct(request, user_id, platform):
    if request.method == "POST":
        data = json.loads(request.body)

        if data == None:
            return HttpResponse("No Data found")

        user_model = AppUserModel.objects.filter(appusers_id=user_id).first()

        # search for product in database
        product = ProductModel()

        product.user_id = user_model

        update_product_variants(product,data["variants"])

        product.shopify_product_id = data["id"]
        product.product_name = data["title"]

        prd_desc = re.compile('<.*?>')
        prd_desc = re.sub(prd_desc, '', data["body_html"])
        product.short_description = prd_desc

        product.link_to_brand = data["vendor"]
        product.product_type = data["product_type"]
        product.gender = data["tags"]
        product.platform = "shopify"
        try:
            product.save()
        except:
            return HttpResponse(send_err_res.raiseDBError("SW"))

        if len(data["images"]) > 0:
            for i in range(len(data["images"])):
                product_files = ProductFilesModel()
                product_files.product_id = product
                update_product_files(product_files, data["images"][i]["src"], data["images"][i]["id"])

    return HttpResponse("Data imported successfully")


@csrf_exempt
def updateProduct(request, user_id, platform):
    if request.method == "POST":
        data = json.loads(request.body)

        if data == None:
            return HttpResponse("No Data found")

        upd_product = ProductModel.objects.filter(shopify_product_id=str(data["id"])).filter(
            deleted=0).first()

        # if Product not found create new product
        if upd_product == None:
            user_model = AppUserModel.objects.filter(appusers_id=user_id).first()

            product = ProductModel()
            product.user_id = user_model

            update_product_variants(product, data["variants"])

            product.shopify_product_id = data["id"]
            product.product_name = data["title"]

            # remove HTML tags from body_html variable
            prd_desc = re.compile('<.*?>')
            prd_desc = re.sub(prd_desc, '', data["body_html"])
            product.short_description = prd_desc

            product.link_to_brand = data["vendor"]
            product.product_type = data["product_type"]
            product.gender = data["tags"]
            product.platform = "shopify"
        else:
            # if product found then update it
            update_product_variants(upd_product, data["variants"])

            upd_product.product_name = data["title"]

            # remove HTML tags from body_html variable
            prd_desc = re.compile('<.*?>')
            prd_desc = re.sub(prd_desc, '', data["body_html"])
            upd_product.short_description = prd_desc

            upd_product.link_to_brand = data["vendor"]
            upd_product.product_type = data["product_type"]
            upd_product.gender = data["tags"]

        if upd_product == None:
            product.save()
            if len(data["images"]) > 0:
                for i in range(len(data["images"])):
                    product_files = ProductFilesModel()
                    product_files.product_id = product
                    update_product_files(product_files, data["images"][i]["src"], data["images"][i]["id"])
        else:
            upd_product.save()

            if len(data["images"]) > 0:
                for i in range(len(data["images"])):
                    product_files = ProductFilesModel.objects.filter(product_id=upd_product.product_id).filter(
                        store_file_id=data["images"][i]["id"]).filter(deleted=0).first()
                    if product_files == None:
                        product_files = ProductFilesModel()
                    product_files.product_id = upd_product
                    update_product_files(product_files, data["images"][i]["src"], data["images"][i]["id"])

    return HttpResponse("Product updated successfully")


@csrf_exempt
def deleteProduct(request, platform):
    data = json.loads(request.body)
    id = data["id"]
    product = ProductModel.objects.filter(shopify_product_id=str(id)).filter(deleted=0).first()
    product.deleted = 1
    product_files = ProductFilesModel.objects.filter(product_id=product.product_id).filter(deleted=0).first()
    product_files.deleted = 1
    try:
        if product != None:
            product.save()

        if product_files != None:
            product_files.save()
    except:
        return HttpResponse(send_err_res.raiseDBError("SW"))

    return HttpResponse("Product deleted successfully")
