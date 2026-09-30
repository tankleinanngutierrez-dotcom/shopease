from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views
urlpatterns=[
 path('admin/',admin.site.urls), path('',views.product_list,name='product_list'),
 path('products/<int:pk>/',views.product_detail,name='product_detail'),
 path('manage/products/',views.product_manage,name='product_manage'),
 path('manage/products/add/',views.product_create,name='product_create'),
 path('manage/products/<int:pk>/edit/',views.product_edit,name='product_edit'),
 path('manage/products/<int:pk>/delete/',views.product_delete,name='product_delete'),
 path('cart/',views.cart,name='cart'), path('cart/add/<int:pk>/',views.add_to_cart,name='add_to_cart'),
 path('cart/item/<int:pk>/',views.update_cart_item,name='update_cart_item'),
 path('cart/item/<int:pk>/remove/',views.remove_cart_item,name='remove_cart_item'),
 path('checkout/',views.checkout,name='checkout'), path('shipping-total/',views.shipping_total,name='shipping_total'),
 path('orders/<int:pk>/confirmation/',views.order_success,name='order_success'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
