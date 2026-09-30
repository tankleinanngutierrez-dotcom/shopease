from django.contrib import admin
from .models import Category,Product,Order,OrderItem
admin.site.register([Category,Product,Order,OrderItem])
