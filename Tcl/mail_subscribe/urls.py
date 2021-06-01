from django.urls import path
from mail_subscribe import views

urlpatterns = [
    path('', views.subscription),
]
