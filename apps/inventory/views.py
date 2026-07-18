from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta, date
from django.db import transaction
from .models import Product, Category, StockMovement, Sale, SaleItem
from .forms import ProductForm, CategoryForm, StockAdjustmentForm, SaleItemForm, SaleForm
from apps.users.models import CustomUser, UserTypes


def user_is_admin(user):
    return user.is_authenticated and user.user_type == UserTypes.ADMIN


@login_required
def dashboard(request):
    # Get key metrics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_items = Product.objects.filter(is_active=True, quantity__lte=F('min_stock_level')).count()

    # Today's sales
    today = timezone.now().date()
    from .models import Sale
    today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
        total=Sum('total_amount'),
        count=Sum('items__quantity')
    )

    # Monthly sales
    month_start = today.replace(day=1)
    monthly_sales = Sale.objects.filter(sale_date__date__gte=month_start).aggregate(
        total=Sum('total_amount'),
        count=Sum('items__quantity')
    )

    # Recent sales
    recent_sales = Sale.objects.select_related('sold_by').order_by('-sale_date')[:10]

    # Low stock products
    low_stock_products = Product.objects.filter(
        is_active=True,
        quantity__lte=F('min_stock_level')
    ).order_by('quantity')[:10]
    
    context = {
        'total_products': total_products,
        'low_stock_items': low_stock_items,
        'today_sales_total': today_sales['total'] or 0,
        'today_sales_count': today_sales['count'] or 0,
        'monthly_sales_total': monthly_sales['total'] or 0,
        'monthly_sales_count': monthly_sales['count'] or 0,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')
    
    products = Product.objects.filter(is_active=True).select_related('category')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if low_stock:
        products = products.filter(quantity__lte=F('min_stock_level'))
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'low_stock': low_stock,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stock_movements = product.stock_movements.select_related('performed_by').order_by('-timestamp')[:20]
    
    context = {
        'product': product,
        'stock_movements': stock_movements,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/product_detail.html', context)


@login_required
def product_create(request):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to create products.')
        return redirect('inventory:product_list')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Create initial stock movement
            if product.quantity > 0:
                StockMovement.objects.create(
                    product=product,
                    quantity_change=product.quantity,
                    reason='purchase',
                    performed_by=request.user
                )
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
def product_update(request, pk):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to update products.')
        return redirect('inventory:product_list')
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            old_quantity = product.quantity
            updated_product = form.save()
            
            # Create stock movement if quantity changed
            if updated_product.quantity != old_quantity:
                difference = updated_product.quantity - old_quantity
                StockMovement.objects.create(
                    product=updated_product,
                    quantity_change=difference,
                    reason='adjustment',
                    performed_by=request.user
                )
            
            messages.success(request, f'Product "{updated_product.name}" updated successfully.')
            return redirect('inventory:product_detail', pk=updated_product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
def product_delete(request, pk):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to delete products.')
        return redirect('inventory:product_list')
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product.name}" deleted successfully.')
        return redirect('inventory:product_list')
    
    context = {
        'product': product,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/product_delete.html', context)


@login_required
def stock_adjust(request, pk):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to adjust stock.')
        return redirect('inventory:product_detail', pk=pk)
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            quantity_change = form.cleaned_data['quantity_change']
            reason = form.cleaned_data['reason']
            notes = form.cleaned_data['notes']
            
            # Update product quantity
            new_quantity = product.quantity + quantity_change
            if new_quantity < 0:
                messages.error(request, 'Stock cannot go below zero.')
                return redirect('inventory:product_detail', pk=pk)
            
            product.quantity = new_quantity
            product.save()
            
            # Create stock movement
            StockMovement.objects.create(
                product=product,
                quantity_change=quantity_change,
                reason=reason,
                notes=notes,
                performed_by=request.user
            )
            
            messages.success(request, f'Stock adjusted successfully. New quantity: {product.quantity}')
            return redirect('inventory:product_detail', pk=pk)
    else:
        form = StockAdjustmentForm()
    
    context = {
        'form': form,
        'product': product,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/stock_adjust.html', context)


@login_required
def low_stock_report(request):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to view low stock reports.')
        return redirect('inventory:dashboard')
    
    products = Product.objects.filter(
        is_active=True,
        quantity__lte=F('min_stock_level')
    ).select_related('category').order_by('quantity')
    
    context = {
        'products': products,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/low_stock_report.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/category_list.html', context)


@login_required
def category_create(request):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to create categories.')
        return redirect('inventory:category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/category_form.html', context)


# Sales Views

@login_required
def sale_create(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        
        # Get cart items from session or POST
        cart = request.session.get('sale_cart', {})
        
        if not cart:
            messages.error(request, 'Your cart is empty. Add products before completing the sale.')
            return redirect('inventory:sale_create')
        
        if sale_form.is_valid():
            try:
                with transaction.atomic():
                    # Create sale
                    sale = sale_form.save(commit=False)
                    sale.sold_by = request.user
                    sale.total_amount = 0
                    sale.save()
                    
                    # Process each item in cart
                    for product_id, item_data in cart.items():
                        product = Product.objects.get(id=product_id)
                        quantity = item_data['quantity']
                        
                        # Check stock
                        if product.quantity < quantity:
                            messages.error(request, f'Not enough stock for {product.name}. Available: {product.quantity}, Requested: {quantity}')
                            sale.delete()
                            return redirect('inventory:sale_create')
                        
                        # Create sale item
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=quantity,
                            unit_price=product.price,
                            total_price=product.price * quantity
                        )
                        
                        # Update product stock
                        product.quantity -= quantity
                        product.save()
                        
                        # Create stock movement
                        StockMovement.objects.create(
                            product=product,
                            quantity_change=-quantity,
                            reason='sale',
                            performed_by=request.user
                        )
                        
                        # Add to sale total
                        sale.total_amount += product.price * quantity
                    
                    sale.save()
                    
                    # Clear cart
                    request.session['sale_cart'] = {}
                    
                    messages.success(request, f'Sale completed successfully! Total: ${sale.total_amount:.2f}')
                    return redirect('inventory:sale_detail', pk=sale.pk)
                    
            except Exception as e:
                messages.error(request, f'Error processing sale: {str(e)}')
                return redirect('inventory:sale_create')
    else:
        sale_form = SaleForm()
    
    cart = request.session.get('sale_cart', {})
    cart_items = []
    cart_total = 0
    
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item_data['quantity']
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'total': item_total
            })
            cart_total += item_total
        except Product.DoesNotExist:
            pass
    
    context = {
        'sale_form': sale_form,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'products': Product.objects.filter(is_active=True).order_by('name'),
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/sale_create.html', context)


@login_required
def sale_add_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            if product.quantity < quantity:
                messages.error(request, f'Not enough stock for {product.name}. Available: {product.quantity}')
            else:
                cart = request.session.get('sale_cart', {})
                
                if product_id in cart:
                    cart[product_id]['quantity'] += quantity
                else:
                    cart[product_id] = {'quantity': quantity}
                
                request.session['sale_cart'] = cart
                messages.success(request, f'Added {quantity} x {product.name} to cart')
                
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
    
    return redirect('inventory:sale_create')


@login_required
def sale_remove_item(request, product_id):
    cart = request.session.get('sale_cart', {})
    
    if product_id in cart:
        del cart[product_id]
        request.session['sale_cart'] = cart
        messages.success(request, 'Item removed from cart')
    
    return redirect('inventory:sale_create')


@login_required
def sale_clear_cart(request):
    request.session['sale_cart'] = {}
    messages.success(request, 'Cart cleared')
    return redirect('inventory:sale_create')


@login_required
def sale_list(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    staff_id = request.GET.get('staff')
    
    sales = Sale.objects.select_related('sold_by').prefetch_related('items__product')
    
    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)
    if staff_id:
        sales = sales.filter(sold_by_id=staff_id)
    
    sales = sales.order_by('-sale_date')
    
    # Get staff members for filter
    from apps.users.models import CustomUser
    staff_members = CustomUser.objects.filter(user_type=UserTypes.STAFF).union(
        CustomUser.objects.filter(user_type=UserTypes.ADMIN)
    )
    
    context = {
        'sales': sales,
        'staff_members': staff_members,
        'date_from': date_from,
        'date_to': date_to,
        'selected_staff': staff_id,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/sale_list.html', context)


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.select_related('product')
    
    context = {
        'sale': sale,
        'items': items,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/sale_detail.html', context)


@login_required
def sales_report(request):
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to view sales reports.')
        return redirect('inventory:dashboard')
    
    period = request.GET.get('period', 'today')
    
    today = timezone.now().date()
    
    if period == 'today':
        date_from = today
        date_to = today
    elif period == 'week':
        date_from = today - timedelta(days=7)
        date_to = today
    elif period == 'month':
        date_from = today.replace(day=1)
        date_to = today
    else:
        date_from = today - timedelta(days=30)
        date_to = today
    
    sales = Sale.objects.filter(
        sale_date__date__gte=date_from,
        sale_date__date__lte=date_to
    )
    
    # Summary stats
    total_sales = sales.aggregate(
        total_amount=Sum('total_amount'),
        total_items=Sum('items__quantity')
    )
    
    # Top selling products
    from django.db.models import Count
    top_products = SaleItem.objects.filter(
        sale__sale_date__date__gte=date_from,
        sale__sale_date__date__lte=date_to
    ).values('product__name', 'product__sku').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    
    # Sales by staff
    sales_by_staff = sales.values('sold_by__id', 'sold_by__email', 'sold_by__first_name', 'sold_by__last_name').annotate(
        total_sales=Sum('total_amount'),
        sale_count=Count('id')
    ).order_by('-total_sales')
    
    context = {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales['total_amount'] or 0,
        'total_items': total_sales['total_items'] or 0,
        'top_products': top_products,
        'sales_by_staff': sales_by_staff,
        'is_admin': user_is_admin(request.user),
    }
    return render(request, 'inventory/sales_report.html', context)
