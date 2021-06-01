from django.db import models

class FAQModel(models.Model):
    class Meta:
        db_table = 'FAQ_table'
    faq_id = models.AutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField()
 
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)


    def __str__(self):
        return f"({self.faqtable_id},{self.question},{self.answer})"