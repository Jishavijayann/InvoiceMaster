"""
URL configuration for customer_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.urls import path
# from customer_manager.customer_manager import views
# urlpatterns = [
#     path('customers/', views.customer_list, name='customer_list'),
#     path('customers/<int:pk>/', views.customer_edit, name='customer_edit'),
#     path('products/', views.product_list, name='product_list'),
#     path('invoices/', views.invoice_list, name='invoice_list'),
#     path('invoices/create/', views.create_invoice, name='create_invoice'),
# ]

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('customers.urls')),
    path('admin/', admin.site.urls),
]