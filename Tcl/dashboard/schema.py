from graphene import ObjectType, String, Schema
import graphene
from datetime import datetime
from product.models import ProductModel,ProductMonthClickCount
from onboarding.models import OnboardingModel
from utilities.mail_notification import sendNotification


class ProductCount(graphene.ObjectType):
    active_prd_cnt = graphene.String()
    total_prd_click=graphene.String()
    over_prd_click=graphene.String()



class Query(ObjectType):
    product_cnt = graphene.List(ProductCount,brand_id=graphene.Int())

    def resolve_product_cnt(root, info,brand_id=None):
        prd_cnt_list = []

        prod_count=ProductModel.objects.filter(deleted=0,status=1)

        if brand_id:
            app_user=OnboardingModel.objects.filter(pk=brand_id,deleted=0)
            prod_count=prod_count.filter(user_id_id=app_user[0].user_id_id)

        ovr_prd_clk=ProductMonthClickCount.objects.filter(product_id__in=prod_count)
        prd_mnt_clk=ovr_prd_clk.filter(month=datetime.now().month)

        prd_cnt = ProductCount(len(prod_count),len(prd_mnt_clk),len(ovr_prd_clk))
        prd_cnt_list.append(prd_cnt)

        return prd_cnt_list


schema = Schema(query=Query)
