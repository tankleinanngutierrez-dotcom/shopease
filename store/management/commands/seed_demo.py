from django.core.management.base import BaseCommand
from store.models import Category,Product
SAMPLES=[
('Tech Essentials','tech-essentials',[('Wireless Mouse','Comfortable silent-click wireless mouse for everyday work.',650,10),('Mechanical Keyboard','Compact mechanical keyboard with tactile switches.',2500,5),('USB-C Hub','7-in-1 USB-C hub for modern laptops.',1200,8),('Webcam','1080p webcam for calls, classes, and streaming.',1800,6)]),
('Workspace','workspace',[('Laptop Stand','Aluminum adjustable stand for a cleaner desk.',900,0),('Desk Lamp','Warm LED desk lamp with adjustable neck.',1100,7),('Notebook Set','Three premium notebooks for notes and planning.',450,14)]),
('Lifestyle','lifestyle',[('Insulated Tumbler','Double-wall tumbler that keeps drinks cool.',750,9),('Travel Pouch','Organized pouch for cables and daily essentials.',520,4),('Everyday Tote','Structured reusable tote with reinforced handles.',680,12)])]
class Command(BaseCommand):
    help='Create ShopEase demo categories and products.'
    def handle(self,*args,**kwargs):
        for cname,slug,products in SAMPLES:
            c,_=Category.objects.get_or_create(slug=slug,defaults={'name':cname});c.name=cname;c.save()
            for name,desc,price,stock in products:
                slug=name.lower().replace(' ','-').replace('/','-')
                Product.objects.update_or_create(name=name,defaults={'category':c,'description':desc,'price':price,'stock':stock,'image':f'products/{slug}.svg','is_active':True})
        self.stdout.write(self.style.SUCCESS('Demo catalog ready.'))
