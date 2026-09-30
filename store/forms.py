import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Product,Order

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','category','description','price','stock','image','is_active']
        labels={'name':'Product name','category':'Category','description':'Description','price':'Price (₱)','stock':'Available stock','image':'Product image','is_active':'Visible in storefront'}
        help_texts={'price':'Enter a positive amount.','stock':'Use 0 for out of stock.','image':'Optional JPG/PNG/WebP product image.'}
        widgets={'name':forms.TextInput(attrs={'placeholder':'e.g. Wireless Mouse','class':'field-input'}),'category':forms.Select(attrs={'class':'field-input'}),'description':forms.Textarea(attrs={'rows':4,'placeholder':'Describe the product...','class':'field-input'}),'price':forms.NumberInput(attrs={'min':'0.01','step':'0.01','class':'field-input'}),'stock':forms.NumberInput(attrs={'min':'0','class':'field-input'}),'image':forms.ClearableFileInput(attrs={'class':'field-input','accept':'image/*'}),'is_active':forms.CheckboxInput(attrs={'class':'toggle'})}
    def clean_price(self):
        v=self.cleaned_data['price']
        if v<=0: raise ValidationError('Price must be greater than 0.')
        return v
    def clean_stock(self):
        v=self.cleaned_data['stock']
        if v<0: raise ValidationError('Stock cannot be negative.')
        return v

class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['customer_name','email','phone','address','city','shipping_method','payment_method']
        labels={'customer_name':'Full name','email':'Email address','phone':'Philippine mobile number','address':'Complete delivery address','city':'City / Municipality','shipping_method':'Shipping method','payment_method':'Payment method'}
        help_texts={'phone':'Format: 09XXXXXXXXX or +639XXXXXXXXX','address':'House/building, street, barangay.','shipping_method':'Express needs a complete address and city.'}
        widgets={'customer_name':forms.TextInput(attrs={'class':'field-input','autocomplete':'name'}),'email':forms.EmailInput(attrs={'class':'field-input','autocomplete':'email'}),'phone':forms.TextInput(attrs={'class':'field-input','placeholder':'09XXXXXXXXX'}),'address':forms.TextInput(attrs={'class':'field-input'}),'city':forms.TextInput(attrs={'class':'field-input'}),'shipping_method':forms.Select(attrs={'class':'field-input','hx-get':'/shipping-total/','hx-trigger':'change','hx-target':'#order-summary','hx-indicator':'#global-indicator'}),'payment_method':forms.Select(attrs={'class':'field-input'})}
    def clean_phone(self):
        phone=self.cleaned_data['phone'].strip()
        if not re.fullmatch(r'(09\d{9}|\+639\d{9})',phone): raise ValidationError('Enter a valid Philippine mobile number: 09XXXXXXXXX or +639XXXXXXXXX.')
        return phone
    def clean(self):
        cleaned=super().clean()
        if cleaned.get('shipping_method')=='express' and (not cleaned.get('address') or not cleaned.get('city')):
            raise ValidationError('Express shipping requires a complete delivery address and city.')
        return cleaned
