from django.urls import path
from . import views
urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('products/', views.product_list, name='product_list'),
    path('invoices/', views.invoice_view, name='invoice_list'),
    
]

