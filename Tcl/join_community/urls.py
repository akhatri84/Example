from django.urls import path

from join_community import views

urlpatterns = [
    path('', views.join_community),
]
