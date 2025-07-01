from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('cart', views.cart_page, name='cart'),
    path('fav', views.fav_page, name='fav'),
    path('fav_view_page', views.fav_view_page, name='fav_view_page'),
    path('remove_fav/<str:fid>/', views.remove_fav, name='remove_fav'),
    path('remove_cart/<str:cid>', views.remove_cart, name='remove_cart'),
    path('collections', views.collections, name='collections'),
    path('collections/<str:name>', views.collectionsview, name='collections'),
    path('collections/<str:cname>/<str:pname>', views.product_details, name='product_details'),
    path('addtocart', views.add_to_cart, name='addtocart'),
    path('place_order/<str:pid>/', views.place_order, name='place_order'),
    path('my-orders/', views.track_orders, name='track_orders'),
    path('order-success/', views.order_success, name='order_success'),
    path('track_view_page', views.track_view_page, name='track_view_page'),
    path('search/', views.search_products, name='search_products'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),]

