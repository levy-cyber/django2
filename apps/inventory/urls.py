from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/stock-adjust/', views.stock_adjust, name='stock_adjust'),
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    # Sales URLs
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/add-item/', views.sale_add_item, name='sale_add_item'),
    path('sales/remove-item/<str:product_id>/', views.sale_remove_item, name='sale_remove_item'),
    path('sales/clear-cart/', views.sale_clear_cart, name='sale_clear_cart'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('reports/sales/', views.sales_report, name='sales_report'),
]
