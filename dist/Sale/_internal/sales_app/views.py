from django.db import transaction, models
from django.db.models import ProtectedError, Sum
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime, time, timedelta
from .forms import ProductForm, SaleItemForm
from .models import Product, Sale, SaleItem
import plotly.express as px
import pandas as pd
from django.forms import modelformset_factory


# 📊 Dashboard
def dashboard(request):
    products = Product.objects.filter(active=True).order_by("-date_added")
    products_count = products.count()
    today = timezone.localdate()
    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))

    sales_today = Sale.objects.filter(
        date__range=(start_of_day, end_of_day)
    ).count()
    total_sales_today_amount = (
        Sale.objects.filter(date__range=(start_of_day, end_of_day))
        .aggregate(total=models.Sum("total_amount"))["total"]
        or 0
    )

    total_month_sales = Sale.objects.filter(date__month=today.month).count()
    total_month_sales_amount = (
        Sale.objects.filter(date__month=today.month)
        .aggregate(total=models.Sum("total_amount"))["total"]
        or 0
    )

    stock_count = sum(p.quantity for p in products)
    low_stock_products = products.filter(
        quantity__lte=models.F("min_quantity")
    )

    context = {
        "products_count": products_count,
        "sales_today": sales_today,
        "stock_count": stock_count,
        "total_month_sales": total_month_sales,
        "total_sales_today_amount": total_sales_today_amount,
        "total_month_sales_amount": total_month_sales_amount,
        "products": products,
        "low_stock_products": low_stock_products,
    }
    return render(request, "sales_app/dashboard.html", context)


# ➕ Add Product
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Product.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Product '{name}' already exists!")
                return redirect("sales_app:add_product")

            form.save()
            messages.success(request, f"Product '{name}' added successfully!")
            return redirect("sales_app:product_list")
    else:
        form = ProductForm()
    return render(request, "sales_app/add_product.html", {"form": form})


# ✏️ Edit Product
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("sales_app:dashboard")
    else:
        form = ProductForm(instance=product)
    context = {"form": form, "product": product}
    return render(request, "sales_app/edit_product.html", context)


# 👁️ View Product
def view_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "sales_app/view_product.html", {"product": product})


# 🗑️ Delete Product
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except ProtectedError:
        product.active = False
        product.save()
        messages.warning(
            request,
            "Product linked to sales; marked as inactive instead."
        )
    return redirect("sales_app:dashboard")


# 💰 Record Sale (Multiple Products)
def record_sale(request):
    SaleItemFormSet = modelformset_factory(
        SaleItem,
        form=SaleItemForm,
        extra=2,
        can_delete=True
    )

    if request.method == "POST":
        formset = SaleItemFormSet(request.POST)
        if formset.is_valid():
            with transaction.atomic():
                # Create the sale
                sale = Sale.objects.create(
                    user=(request.user
                          if request.user.is_authenticated else None),
                    total_amount=0
                )

                total = Decimal(0)
                for form in formset:
                    if (form.cleaned_data and
                            not form.cleaned_data.get("DELETE", False)):
                        product = form.cleaned_data["product"]
                        qty = form.cleaned_data["quantity"]

                        if product.quantity < qty:
                            error_msg = (
                                f"Not enough stock for {product.name}."
                            )
                            messages.error(request, error_msg)
                            transaction.set_rollback(True)
                            return redirect("sales_app:record_sale")

                        subtotal = product.price * qty
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=qty,
                            subtotal=subtotal
                        )

                        # Reduce stock
                        product.quantity -= qty
                        product.save()
                        total += subtotal

                sale.total_amount = total
                sale.save()

                success_msg = f"Sale recorded successfully (Total: {total})"
                messages.success(request, success_msg)
                return redirect("sales_app:dashboard")
    else:
        formset = SaleItemFormSet(queryset=SaleItem.objects.none())

    return render(request, "sales_app/record_sale.html", {"formset": formset})


# 📜 View Sales
def view_sales(request):
    filter_option = request.GET.get('filter', 'all')
    today = timezone.now().date()

    # Apply filters
    if filter_option == 'day':
        sales = Sale.objects.filter(date__date=today)
    elif filter_option == 'week':
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        sales = Sale.objects.filter(date__date__range=[start_week, end_week])
    elif filter_option == 'month':
        sales = Sale.objects.filter(date__month=today.month)
    else:
        sales = Sale.objects.all()

    # Calculate total sales amount
    total_sales_amount = (
        sales.aggregate(total=Sum('total_amount'))['total'] or 0
    )

    # Attach related SaleItems (using related_name='items')
    for sale in sales:
        sale.items_with_totals = sale.items.annotate(total_val=Sum('subtotal'))

    context = {
        'sales': sales,
        'filter_option': filter_option,
        'total_sales_amount': total_sales_amount,
    }
    return render(request, 'sales_app/view_sales.html', context)


# 🧾 Print Receipt
def print_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sales_app/print_receipt.html', {'sale': sale})


# 📥 Download Receipt
def download_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    html = render_to_string('sales_app/print_receipt.html', {'sale': sale})
    response = HttpResponse(html, content_type='application/octet-stream')
    filename = f'receipt_{sale.id}.html'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# 🗑️ Delete Sale
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    return redirect('sales_app:view_sales')


# Other static pages
def reports(request): return render(request, "sales_app/reports.html")
def customers(request): return render(request, "sales_app/customers.html")
def suppliers(request): return render(request, "sales_app/suppliers.html")
def expenses(request): return render(request, "sales_app/expenses.html")
def settings_view(request): return render(request, "sales_app/settings.html")


# 📦 Product List with search
def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.filter(active=True)
    if query:
        products = products.filter(name__icontains=query)

    context = {'products': products, 'query': query}
    return render(request, 'sales_app/product_list.html', context)


def sales_report(request):
    """
    Report that shows total quantity, total sales, and top 10
    best-selling products.
    """
    # Aggregate SaleItem by product name
    qs = (
        SaleItem.objects
        .select_related('product')
        .values('product__id', 'product__name')
        .annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('subtotal')
        )
        .order_by('-total_quantity')
    )

    df = pd.DataFrame(list(qs))

    top_sales_chart = None
    sales_summary = {}

    if not df.empty:
        top_10 = df.head(10)

        # ✅ Create Plotly bar chart
        fig = px.bar(
            top_10,
            x='product__name',
            y='total_quantity',
            title='Top 10 Selling Products',
            labels={
                'product__name': 'Product',
                'total_quantity': 'Quantity Sold'
            },
            text='total_quantity',
        )
        fig.update_traces(marker_color='lightgreen', textposition='outside')
        fig.update_layout(
            title_x=0.5,
            title_font=dict(size=22),
            yaxis=dict(title='Quantity Sold'),
            xaxis=dict(title='Product')
        )

        top_sales_chart = fig.to_html(full_html=False)

        # Summary
        sales_summary = {
            'total_products': df.shape[0],
            'total_quantity_sold': int(df['total_quantity'].sum()),
            'total_sales_value': float(df['total_amount'].sum() or 0),
        }

    else:
        sales_summary = {
            'total_products': 0,
            'total_quantity_sold': 0,
            'total_sales_value': 0,
        }

    return render(request, 'sales_app/reports.html', {
        'top_sales_chart': top_sales_chart,
        'sales_summary': sales_summary,
    })
