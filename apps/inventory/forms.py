from django import forms
from .models import Product, Category, StockMovement, Sale, SaleItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'barcode', 'category', 'description', 'price', 'cost', 
                  'quantity', 'min_stock_level', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'sku': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'barcode': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'image': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['quantity_change', 'reason', 'notes']
        widgets = {
            'quantity_change': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'reason': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }


class SaleItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'select select-bordered w-full product-select'}),
        empty_label="Select a product"
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '1'})
    )


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['payment_method', 'notes']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
        }
