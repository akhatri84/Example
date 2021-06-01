from django.db import models

class ImpactIndicatorModel(models.Model):
    class Meta:
        db_table = 'impact_indicator'
    impact_indicator_id = models.AutoField(primary_key=True)
    title = models.TextField(null=False)
    blog_title = models.TextField(null=False)
    blog_subject=models.TextField(null=True)
    description = models.TextField(null=False)
    blog_description = models.TextField(null=False)
    url = models.TextField(null=True)
    shop_now_url = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)


    def __str__(self):
        return f"({self.title},{self.description},{self.brands_doing},{self.url})"