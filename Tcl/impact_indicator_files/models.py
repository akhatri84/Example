from django.db import models

from impact_indicator.models import ImpactIndicatorModel


class ImpactIndicatorFilesModel(models.Model):
    impactindicatorfiles_id = models.AutoField(primary_key=True)
    impact_indicator = models.ForeignKey(ImpactIndicatorModel, on_delete=models.CASCADE, null=False)
    file_type = models.TextField()
    file_extension = models.TextField()
    aws_file_url = models.TextField()
    file_size = models.TextField()
    impactindicatorfile_name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    def __str__(self):
        return f"({self.product_id},{self.file_type},{self.aws_file_url},{self.file_size})"

    class Meta:
        db_table = 'impact_indicator_files'

