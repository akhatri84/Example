from django.db import models
from django.db.models.signals import pre_save

from app_user.models import AppUserModel
from utilities.slug_generator import unique_slug_generator


class ProductModel(models.Model):
    class Meta:
        db_table = 'product'

    product_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel, on_delete=models.CASCADE, null=False)
    supply_chain_id = models.IntegerField(null=True)
    product_name = models.TextField(null=False)
    short_description = models.TextField(null=False)
    detail_description = models.TextField(null=True)
    type_of_fashion_product = models.TextField(null=True)
    product_accessories = models.TextField(null=True)
    product_weight = models.TextField(null=False)
    yearly_amount_of_items_procured = models.TextField(null=False)
    average_lifetime_of_your_product = models.TextField(null=True, blank=True)
    end_of_life_biodegradable = models.BooleanField(default=False)
    end_of_life_recyclable = models.BooleanField(default=False)
    end_of_life_product_as_a_service = models.BooleanField(default=False)
    end_of_life_repair_service_brand = models.BooleanField(default=False)
    end_of_life_others = models.TextField()
    link_to_brand = models.TextField(null=True)
    gender = models.TextField()
    transparency_score = models.TextField()
    status = models.BooleanField(default=False)
    shopify_product_id = models.TextField()
    platform = models.TextField(default="TCL")
    price = models.CharField(max_length=10, default="0,0")
    click_count = models.IntegerField(default=0)
    product_link = models.TextField(null=True)
    biobased_material = models.BooleanField(default=False)
    refurbished_material = models.BooleanField(default=False)
    reused_material = models.BooleanField(default=False)
    recycled_material = models.BooleanField(default=False)
    vegan = models.BooleanField(default=False)
    second_life_possible = models.BooleanField(default=False)
    social_impact = models.TextField(null=True)
    organic_fiber = models.BooleanField(default=False)
    showon_landing_page = models.BooleanField(default=False)
    colors = models.TextField(null=True)
    kgco2 = models.FloatField(null=True)
    liter = models.FloatField(null=True)
    kmtravel = models.FloatField(null=True)
    slug = models.SlugField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    def __str__(self):
        return f"({self.product_name},{self.short_description},{self.type_of_fashion_product})"


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, "product")


pre_save.connect(pre_save_receiver, sender=ProductModel)


class AttributeModel(models.Model):
    attribute_id = models.AutoField(primary_key=True)
    attribute_name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "attribute"


class AttributeValueModel(models.Model):
    attribute_value_id = models.AutoField(primary_key=True)
    attribute = models.ForeignKey(AttributeModel, on_delete=models.CASCADE)
    value = models.TextField()
    slug = models.SlugField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "attribute_value"


def pre_save_att_val_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, "attribute_value")


pre_save.connect(pre_save_att_val_receiver, sender=AttributeValueModel)


class ProductAttributeModel(models.Model):
    product_attribute_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValueModel, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "product_attribute"


class ProductMonthClickCount(models.Model):
    product_month_click_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    day = models.IntegerField(default=0)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    ip_address=models.CharField(max_length=20,default="0:0:0:0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "product_month_click"
