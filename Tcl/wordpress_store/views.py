from django.utils import timezone
from django.shortcuts import HttpResponse
from product.models import ProductModel
from product_files.models import ProductFilesModel
from api_config.models import ApiConfigModel
from app_user.models import AppUserModel
from ErrorHandler import send_err_res

import json

import re
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def createWordpressProduct(request,user_id): 
    if request.method == "POST":
        data = json.loads(request.body)

        if len(data) == 0:
            return GraphQLError("No Data found")
        else:
            product = ProductModel()

            user = AppUserModel.objects.filter(appusers_id=user_id).first()

            product.user_id = user

            for key in data.keys():                      
                if key == "id":
                    product.shopify_product_id = data["id"]
                if key == "name":
                    product.product_name =  data["name"]
                if key == "short_description":
                    prd_desc = re.compile('<.*?>')
                    prd_desc = re.sub(prd_desc, '', data["short_description"])
                    product.short_description = prd_desc
                if key == "type":
                    product.product_type = data["type"]
                if key == "weight":
                    product.product_weight = data["weight"]
                if key == "price":
                    product.price = int(float(data["price"]))
                if key == "permalink":
                    product.product_link = data["permalink"]  
                if key == "status":           
                    if data[key] == "publish":
                            product.status = True
            product.platform = "wordpress"
            product.created_at = timezone.now()
            product.updated_at = timezone.now()
            product.updated_by = user.appusers_id
            product.deleted = 0
            try:
                product.save()
            except:
                return HttpResponse(send_err_res.raiseDBError("SW"))                         
            if len(data["images"]) == 1:
                product_files = ProductFilesModel() 
                product_files.product_id = product
                imgsrc = data['images'][0]['src']
                filename = imgsrc.split('/')[-1].split('?')[0]
                file_extention = filename.split('.')[1]
                product_files.file_extension = file_extention
                product_files.aws_file_url = imgsrc
                product_files.file_extension = file_extention
                product_files.file_type = "pic"
                product_files.store_file_id = str(data['images'][0]['id'])  
                product_files.created_at = timezone.now()
                product_files.updated_at = timezone.now()
                product_files.updated_by = user.appusers_id
                product_files.deleted = 0     
            try:
                product_files.save()
            except:
                return HttpResponse(send_err_res.raiseDBError("SW"))     
    return HttpResponse("Data imported successfully")

@csrf_exempt
def updateWordpressProduct(request, user_id):      
    if request.method == "POST":
        data = json.loads(request.body)

    if len(data) == 0:
            return HttpResponse("No Data found")
    else:
        user = AppUserModel.objects.filter(appusers_id=user_id).first()   

        upd_product = ProductModel.objects.filter(shopify_product_id=str(data["id"])).filter(deleted=0).first()

        if upd_product == None:  
            product = ProductModel() 
            product.user_id = user               
            for key in data.keys():                      
                if key == "id":
                    product.shopify_product_id = data["id"]
                if key == "name":
                    product.product_name =  data["name"]
                if key == "short_description":
                    prd_desc = re.compile('<.*?>')
                    prd_desc = re.sub(prd_desc, '', data["short_description"])
                    product.short_description = prd_desc
                if key == "type":
                    product.product_type = data["type"]
                if key == "weight":
                    product.product_weight = data["weight"]
                if key == "price":
                    product.price = int(float(data["price"]))
                if key == "permalink":
                    product.product_link = data["permalink"]
                if key == "status":           
                    if data[key] == "publish":
                            product.status = True
          
            product.created_at = timezone.now()
            product.updated_at = timezone.now()
            product.updated_by = user.appusers_id
            product.deleted = 0

            try:
                product.save()
            except:
                return HttpResponse(send_err_res.raiseDBError("SW"))                   
        else:
            upd_product.user_id = user     
            for key in data.keys():                 
                if key == "name":
                    upd_product.product_name =  data["name"]
                if key == "short_description":
                    prd_desc = re.compile('<.*?>')
                    prd_desc = re.sub(prd_desc, '', data["short_description"])
                    upd_product.short_description = prd_desc
                if key == "type":
                    upd_product.product_type = data["type"]
                if key == "weight":
                    upd_product.product_weight = data["weight"]
                if key == "price":
                    upd_product.price = int(float(data["price"]))
                if key == "permalink":
                    upd_product.product_link = data["permalink"]
                if key == "status":           
                    if data[key] == "publish":
                            upd_product.status = True

            upd_product.updated_at = timezone.now()
            upd_product.updated_by = user.appusers_id

            try:
                upd_product.save()
            except:
                return HttpResponse(send_err_res.raiseDBError("SW"))  

        if len(data["images"]) == 1:
            if upd_product == None:
                product_files = ProductFilesModel()
                product_files.product_id = product
                product_files.created_at = timezone.now()
                product.deleted = 0
            else:
                product_files = ProductFilesModel.objects.filter(product_id=upd_product.product_id,deleted=0).first()
            product_files.updated_by = user.appusers_id
            product_files.updated_at = timezone.now()
            imgsrc = data['images'][0]['src']
            filename = imgsrc.split('/')[-1].split('?')[0]
            file_extention = filename.split('.')[1]
            product_files.file_extension = file_extention
            product_files.aws_file_url = imgsrc
            product_files.file_extension = file_extention
            product_files.file_type = "pic"
            product_files.store_file_id = str(data['images'][0]['id'])        
            try:
                product_files.save()
            except:
                return HttpResponse(send_err_res.raiseDBError("SW"))
    return HttpResponse("Product updated successfully")

@csrf_exempt
def deleteWordpressProduct(request): 
    if request.method == "POST":
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

