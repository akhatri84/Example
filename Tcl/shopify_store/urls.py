from django.urls import path
from shopify_store import views

urlpatterns = [
    path('create/<int:user_id>/<str:platform>', views.createProduct, name='createproduct'),
    path('update/<int:user_id>/<str:platform>', views.updateProduct, name='updateproduct'),
    path('delete/<str:platform>', views.deleteProduct, name='deleteproduct'),
]
