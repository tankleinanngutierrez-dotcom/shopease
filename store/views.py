from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import ProductForm,OrderForm
from .models import Category,Product,Order,OrderItem

CART='shopease_cart'
def is_htmx(request): return request.headers.get('HX-Request')=='true'
def cart_data(request): return request.session.get(CART,{})
def cart_count(request): return sum(int(v) for v in cart_data(request).values())
def cart_lines(request):
    data=cart_data(request); ids=[int(k) for k in data]
    products=Product.objects.filter(id__in=ids,is_active=True)
    found={str(p.pk):p for p in products}; lines=[]; stale=[]
    for k,q in data.items():
        p=found.get(k)
        if not p: stale.append(k); continue
        q=int(q); lines.append({'product':p,'quantity':q,'subtotal':p.price*q})
    return lines,stale

def totals(request):
    lines,_=cart_lines(request); subtotal=sum((x['subtotal'] for x in lines),Decimal('0'))
    shipping=Decimal('0') if subtotal>=2000 else (Decimal('120') if subtotal else Decimal('0'))
    return subtotal,shipping,subtotal+shipping

def save_cart(request,data): request.session[CART]=data; request.session.modified=True

def product_list(request):
    qs=Product.objects.filter(is_active=True).select_related('category')
    search=request.GET.get('q','').strip(); category=request.GET.get('category',''); sort=request.GET.get('sort','newest')
    if search: qs=qs.filter(Q(name__icontains=search)|Q(description__icontains=search))
    if category: qs=qs.filter(category__slug=category)
    qs={'price_low':qs.order_by('price'),'price_high':qs.order_by('-price'),'newest':qs.order_by('-date_created')}.get(sort,qs)
    from django.core.paginator import Paginator
    paginator=Paginator(qs,9); page=paginator.get_page(request.GET.get('page'))
    ctx={'page_obj':page,'products':page.object_list,'categories':Category.objects.all(),'q':search,'category':category,'sort':sort,'result_count':qs.count(),'cart_count':cart_count(request)}
    if is_htmx(request): return render(request,'store/partials/_product_grid.html',ctx)
    return render(request,'store/product_list.html',ctx)

def product_detail(request,pk):
    p=get_object_or_404(Product.objects.select_related('category'),pk=pk,is_active=True)
    if request.method=='POST':
        try: q=int(request.POST.get('quantity','1'))
        except ValueError: q=0
        if q<1 or q>p.stock:
            msg='Choose a quantity within the available stock.'
            return render(request,'store/partials/_inline_notice.html',{'error':msg}) if is_htmx(request) else render(request,'store/product_detail.html',{'product':p,'error':msg})
        data=cart_data(request); data[str(pk)]=int(data.get(str(pk),0))+q
        if data[str(pk)]>p.stock:
            data[str(pk)]=p.stock
            msg='Your cart quantity cannot exceed available stock.'
            return render(request,'store/partials/_inline_notice.html',{'error':msg}) if is_htmx(request) else render(request,'store/product_detail.html',{'product':p,'error':msg})
        save_cart(request,data)
        if is_htmx(request): return render(request,'store/partials/_cart_feedback.html',{'product':p,'cart_count':cart_count(request)})
        messages.success(request,f'{p.name} added to your cart.')
        return redirect('product_detail',pk=pk)
    return render(request,'store/product_detail.html',{'product':p,'cart_count':cart_count(request)})

def add_to_cart(request,pk):
    if request.method!='POST': return redirect('product_list')
    p=get_object_or_404(Product,pk=pk,is_active=True); data=cart_data(request)
    try:q=int(request.POST.get('quantity','1'))
    except ValueError:q=0
    current=int(data.get(str(pk),0))
    if q<1 or current+q>p.stock:
        return render(request,'store/partials/_cart_feedback.html',{'error':f'Only {p.stock-current} more available.','cart_count':cart_count(request)})
    data[str(pk)]=current+q; save_cart(request,data)
    response=render(request,'store/partials/_cart_feedback.html',{'product':p,'cart_count':cart_count(request)})
    response['HX-Trigger']='cartUpdated'
    return response

def cart(request):
    lines,stale=cart_lines(request)
    if stale:
        data=cart_data(request)
        for k in stale:data.pop(k,None)
        save_cart(request,data)
        messages.warning(request,'One or more cart items became unavailable and were removed from your cart.')
    subtotal,shipping,total=totals(request)
    ctx={'lines':lines,'subtotal':subtotal,'shipping':shipping,'total':total,'cart_count':cart_count(request)}
    return render(request,'store/cart.html',ctx)

def update_cart_item(request,pk):
    if request.method not in ['PUT','POST']: return redirect('cart')
    p=get_object_or_404(Product,pk=pk,is_active=True); data=cart_data(request)
    try:q=int(request.POST.get('quantity') or request.body.decode().split('=')[-1])
    except Exception:q=0
    if q<1: return remove_cart_item(request,pk)
    if q>p.stock:
        return render(request,'store/partials/_cart_container.html',{'lines':cart_lines(request)[0],'subtotal':totals(request)[0],'shipping':totals(request)[1],'total':totals(request)[2],'cart_count':cart_count(request),'error':f'{p.name} only has {p.stock} in stock.'})
    data[str(pk)]=q;save_cart(request,data)
    return render(request,'store/partials/_cart_container.html',{'lines':cart_lines(request)[0],'subtotal':totals(request)[0],'shipping':totals(request)[1],'total':totals(request)[2],'cart_count':cart_count(request)})

def remove_cart_item(request,pk):
    data=cart_data(request); data.pop(str(pk),None); save_cart(request,data)
    if is_htmx(request):
        return render(request,'store/partials/_cart_container.html',{'lines':cart_lines(request)[0],'subtotal':totals(request)[0],'shipping':totals(request)[1],'total':totals(request)[2],'cart_count':cart_count(request)})
    return redirect('cart')

def product_manage(request):
    q=request.GET.get('q','').strip(); qs=Product.objects.select_related('category')
    if q:qs=qs.filter(Q(name__icontains=q)|Q(category__name__icontains=q))
    ctx={'products':qs,'q':q}
    if is_htmx(request):return render(request,'store/partials/_management_table.html',ctx)
    return render(request,'store/product_manage.html',ctx)

def product_create(request):
    form=ProductForm(request.POST or None,request.FILES or None)
    if request.method=='POST':
        if form.is_valid():
            p=form.save(); messages.success(request,f'{p.name} was added to the catalog.');
            return redirect('product_manage')
        if is_htmx(request): return render(request,'store/partials/_product_form.html',{'form':form,'title':'Add product'})
    return render(request,'store/product_form.html',{'form':form,'title':'Add product'})

def product_edit(request,pk):
    p=get_object_or_404(Product,pk=pk); form=ProductForm(request.POST or None,request.FILES or None,instance=p)
    if request.method=='POST' and form.is_valid():
        form.save();messages.success(request,f'{p.name} was updated.');return redirect('product_manage')
    if request.method=='POST' and is_htmx(request):return render(request,'store/partials/_product_form.html',{'form':form,'title':f'Edit {p.name}'})
    return render(request,'store/product_form.html',{'form':form,'title':f'Edit {p.name}'})

def product_delete(request,pk):
    p=get_object_or_404(Product,pk=pk);p.delete()
    if is_htmx(request):return render(request,'store/partials/_management_table.html',{'products':Product.objects.select_related('category'),'q':''})
    return redirect('product_manage')

def shipping_total(request):
    subtotal,shipping,total=totals(request)
    if request.GET.get('shipping_method')=='express' and subtotal: shipping=Decimal('250'); total=subtotal+shipping
    return render(request,'store/partials/_order_summary.html',{'subtotal':subtotal,'shipping':shipping,'total':total})

def checkout(request):
    lines,stale=cart_lines(request)
    if stale:
        data=cart_data(request)
        for k in stale:data.pop(k,None)
        save_cart(request,data)
        lines,_=cart_lines(request)
    if not lines:return redirect('cart')
    form=OrderForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            ids=[x['product'].pk for x in lines]; locked={p.pk:p for p in Product.objects.select_for_update().filter(pk__in=ids)}
            for line in lines:
                p=locked.get(line['product'].pk)
                if not p or line['quantity']>p.stock:
                    form.add_error(None,f'{line["product"].name} no longer has enough stock. Please review your cart.')
                    break
            else:
                order=form.save(commit=False); subtotal=sum((x['subtotal'] for x in lines),Decimal('0')); ship=Decimal('250') if order.shipping_method=='express' else (Decimal('120') if subtotal<2000 else Decimal('0')); order.total=subtotal+ship;order.save()
                for line in lines:
                    p=locked[line['product'].pk];OrderItem.objects.create(order=order,product=p,quantity=line['quantity'],unit_price=p.price);p.stock-=line['quantity'];p.save(update_fields=['stock'])
                request.session.pop(CART,None);messages.success(request,'Order placed successfully!')
                if is_htmx(request):
                    return HttpResponse(status=200,headers={'HX-Redirect':reverse('order_success',kwargs={'pk':order.pk})})
                return redirect('order_success',pk=order.pk)
    ctx={'form':form,'lines':lines,'subtotal':totals(request)[0],'shipping':totals(request)[1],'total':totals(request)[2],'cart_count':cart_count(request)}
    if request.method=='POST' and is_htmx(request):return render(request,'store/partials/_checkout_form.html',ctx)
    return render(request,'store/checkout.html',ctx)

def order_success(request,pk):
    order=get_object_or_404(Order.objects.prefetch_related('items__product'),pk=pk);return render(request,'store/order_success.html',{'order':order,'cart_count':cart_count(request)})
