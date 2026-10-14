from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:key>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('cart/coupon/remove/', views.remove_coupon, name='remove_coupon'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
    path('track-order/', views.track_order, name='track_order'),
    
    # Language Switcher
    path('switch-language/<str:lang>/', views.switch_language, name='switch_language'),
]
