from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Customer, Product, Invoice, InvoiceItem
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import datetime
import json
from django.db.models import Q

# Customer Views
@csrf_exempt
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        search_query = request.GET.get('q', '')
        if search_query:
            customers = customers.filter(
                Q(name__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return render(request, 'customers/customer_list.html', {'customers': customers})

    if request.method == 'POST':
        data = json.loads(request.body)
        customer = Customer.objects.create(
            name=data['name'],
            phone_number=data['phone_number'],
            email=data['email']
        )
        return JsonResponse({'id': customer.id, 'status': 'created'})

@csrf_exempt
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        customer.name = data['name']
        customer.phone_number = data['phone_number']
        customer.email = data['email']
        customer.save()
        return JsonResponse({'status': 'updated'})

# Product Views
@csrf_exempt
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        search_query = request.GET.get('q', '')
        if search_query:
            products = products.filter(
                Q(product_name__icontains=search_query) |
                Q(rate__icontains=search_query) |
                Q(tax__icontains=search_query)
            )
        return render(request, 'products/products_list.html', {'products': products})

    if request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(
            product_name=data['product_name'],
            rate=data['rate'],
            tax=data['tax']
        )
        return JsonResponse({'id': product.id, 'status': 'created'})

    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            product = Product.objects.get(id=data['id'])
            product.product_name = data.get('product_name', product.product_name)
            product.rate = data.get('rate', product.rate)
            product.tax = data.get('tax', product.tax)
            product.save()
            return JsonResponse({'id': product.id, 'status': 'updated'})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

# Invoice Views

@csrf_exempt
def invoice_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if data.get('action') == 'save_all':
                return JsonResponse({'status': 'success', 'message': 'All invoices saved successfully!'}, status=200)

            customer_id = data.get('customer_id')
            if not customer_id:
                return JsonResponse({'error': 'customer_id is required'}, status=400)

            customer = Customer.objects.get(id=customer_id)
            if Invoice.objects.filter(customer=customer).exists():
                return JsonResponse({'error': 'Customer already has an invoice.'}, status=400)

            last_invoice = Invoice.objects.last()
            next_invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1}"

            invoice = Invoice.objects.create(
                customer=customer,
                invoice_number=next_invoice_number
            )

            total_amount = Decimal(0) 

            for item in data['items']:
                product = Product.objects.get(id=item['product_id'])
                quantity = Decimal(item['quantity'])
                rate = product.rate
                tax = product.tax
                subtotal = (quantity * rate) + tax  
                total_amount += subtotal

                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    rate=rate,
                    tax=tax,
                    subtotal=subtotal
                )

            invoice.total = total_amount
            invoice.save()

            return JsonResponse({'id': invoice.invoice_number, 'status': 'created'}, status=201)

        except Exception as e:
            print(e, "Error in POST request")
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'GET':
        query = request.GET.get('query', '')
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        invoices = Invoice.objects.prefetch_related('items')

        if query:
            invoices = invoices.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query)
            )

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                invoices = invoices.filter(date__gte=start_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid start_date format. Use YYYY-MM-DD.'}, status=400)

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                invoices = invoices.filter(date__lte=end_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid end_date format. Use YYYY-MM-DD.'}, status=400)

   
        invoice_data = []
        for invoice in invoices:
            items = invoice.items.all()
            invoice_data.append({
                'invoice_number': invoice.invoice_number,
                'customer': invoice.customer.name,
                'date': invoice.date,
                'total': invoice.total,
                'items': [
                    {
                        'product_name': item.product.product_name,
                        'quantity': item.quantity,
                        'rate': item.rate,
                        'tax': item.tax,
                        'subtotal': item.subtotal
                    } for item in items
                ]
            })

        customers = Customer.objects.all()
        products = Product.objects.all()

        return render(
            request,
            'invoices/invoice_list.html',
            {
                'invoices': invoice_data,
                'customers': customers,
                'products': products,
                'query': query,
                'start_date': start_date,
                'end_date': end_date,
            }
        )