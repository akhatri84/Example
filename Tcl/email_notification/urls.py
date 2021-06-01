from django.urls import path
from .views import product_summary_notification
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('prodsumm',csrf_exempt(product_summary_notification),name="prod-summary"),
]