from django.urls import path
from wordpress_store import views

urlpatterns = [
    path('create/<int:user_id>', views.createWordpressProduct, name='createwordpressproduct'),
    path('update/<int:user_id>', views.updateWordpressProduct, name='updatewordpressproduct'),
    path('delete', views.deleteWordpressProduct, name='deletewordpressproduct'),
]
