from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='index'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
    path('products/', views.product_management, name='product_management'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('categories/', views.category_management, name='category_management'),
    path('coupons/', views.coupon_management, name='coupon_management'),
]
