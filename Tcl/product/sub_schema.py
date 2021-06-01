from product.models import ProductAttributeModel



def addattribute(kwargs,attribute,product_id,crup):

    if attribute in kwargs:

        if crup==0:
            if attribute=="sizes":
                ProductAttributeModel.objects.filter(attribute_value__attribute_id=1,product_id=product_id).delete()
                attributes = kwargs["sizes"]
            elif attribute=="product_type":
                ProductAttributeModel.objects.filter(attribute_value__attribute_id=2,product_id=product_id).delete()
                attributes = kwargs["product_type"]
            #elif attribute=="colors":
            #    ProductAttributeModel.objects.filter(attribute_value__attribute_id=3,product_id=product_id).delete()
            #    attributes = kwargs["colors"]


        if attribute=="sizes":
            attributes = kwargs["sizes"]
        elif attribute=="product_type":
            attributes = kwargs["product_type"]
        #elif attribute=="colors":
        #    attributes = kwargs["colors"]



        for attribute_id in attributes:

            productAttribute = ProductAttributeModel()
            productAttribute.product_id = product_id
            productAttribute.attribute_value_id = attribute_id
            productAttribute.save()
