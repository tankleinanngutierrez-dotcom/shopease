from django.db import models
from django.urls import reverse

class Category(models.Model):
    name=models.CharField(max_length=80)
    slug=models.SlugField(max_length=90,unique=True)
    class Meta: ordering=['name']
    def __str__(self): return self.name

class Product(models.Model):
    name=models.CharField(max_length=160)
    category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    stock=models.PositiveIntegerField(default=0)
    image=models.ImageField(upload_to='products/',blank=True,null=True)
    is_active=models.BooleanField(default=True)
    date_created=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-date_created']
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('product_detail',args=[self.pk])
    @property
    def stock_label(self):
        if self.stock<=0:return 'Out of Stock'
        if self.stock<=5:return 'Low Stock'
        return 'In Stock'
    @property
    def stock_class(self):
        return {'Out of Stock':'out','Low Stock':'low','In Stock':'in'}[self.stock_label]

class Order(models.Model):
    SHIPPING=[('standard','Standard · 3–5 days'),('express','Express · 1–2 days')]
    PAYMENT=[('cod','Cash on Delivery'),('later','Pay Later')]
    STATUS=[('pending','Pending'),('processing','Processing'),('completed','Completed')]
    customer_name=models.CharField(max_length=120); email=models.EmailField(); phone=models.CharField(max_length=16)
    address=models.CharField(max_length=255); city=models.CharField(max_length=100)
    shipping_method=models.CharField(max_length=20,choices=SHIPPING,default='standard')
    payment_method=models.CharField(max_length=20,choices=PAYMENT,default='cod')
    total=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    status=models.CharField(max_length=20,choices=STATUS,default='pending'); date_created=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'SE-{self.pk:05d}'

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField(); unit_price=models.DecimalField(max_digits=10,decimal_places=2)
    @property
    def subtotal(self): return self.quantity*self.unit_price
