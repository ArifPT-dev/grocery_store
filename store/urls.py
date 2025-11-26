from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('branches/near/', views.find_nearby_branches, name='find_nearby'),
    path('branch/select/<int:branch_id>/', views.select_branch, name='select_branch'),
    path('branch/<int:branch_id>/products/', views.product_by_branch, name='product_by_branch'),
    path('cart/', views.cart_page, name='cart'),
    path('cart/add/<int:branch_id>/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("orders/", views.my_orders, name="my_orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
]

