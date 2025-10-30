from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.db.models import Avg
from shop.forms import CustomUserForm
from django.contrib.auth import authenticate,login,logout
import json
import random
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .utils import generate_otp
from .forms import ReviewForm

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'shop/index.html',{'products':products})

def cart_page(request):
     if request.user.is_authenticated:
         cart=Cart.objects.filter(user=request.user)
         return render(request, 'shop/cart.html',{'cart':cart})
     else:
         return redirect("/")
     
def remove_fav(request,fid):
    item=Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/fav_view_page")

def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")

def fav_view_page(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")

def fav_page(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_id=data['pid']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user,product_id=product_id)
                    return JsonResponse({'status':'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status':'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)
     
def add_to_cart(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_qty=(data['product_qty'])
            product_id=(data['pid'])
            # print(request.user.id)
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status':'Product Added to Cart'}, status=200)
                    else:
                        if product_status.quantity>=product_qty:
                            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                            return JsonResponse({'status':'Product Added to Cart'}, status=200)
                        else:
                            return JsonResponse({'status':'product Stock Not Available'},status=200)
        else:
            return JsonResponse({'status':'Login to Add Cart'})
    else:
        return JsonResponse({'status':'Ivalid Access'}, status=200)
         
    
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged in Successfully")
    return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
         return redirect("/")
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,'Invalid User None or Password')
                return redirect('/login')
        return render(request, 'shop/login.html')

def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You can Login Now..!")
            return redirect('/login')
    return render(request, 'shop/register.html',{'form':form})

def collections(request):
    category = Category.objects.filter(status=0)
    return render(request, 'shop/collections.html', {'category':category})

def collectionsview(request, name):
    if(Category.objects.filter(name=name,status=0)):
        products = Product.objects.filter(category__name=name).annotate(avg_rating=Avg('reviews__rating'))
        return render(request, 'shop/products/index.html', {'products':products, 'category_name':name})
    else:
         messages.warning(request, "No such category found")
         return redirect('collections') 
    
def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products = Product.objects.filter(name=pname,status=0).first()
            reviews = products.reviews.all().order_by('-created_at')

        if request.method == "POST" and request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product = products
                review.save()
                messages.success(request, "Review submitted successfully.")
                return redirect(request.path_info)
        else:
            form = ReviewForm()

        return render(request, 'shop/products/product_details.html', {
            'products': products,
            'form': form,
            'reviews': reviews
        })
    else:
        messages.error(request, "Product not found.")
        return redirect('collections')

@login_required
def place_order(request, pid):
    product = Product.objects.get(id=pid)

    if request.method == 'POST':
        qty = int(request.POST['quantity'])
        address = request.POST['address']
        payment = request.POST.get('payment_method')
        instructions = request.POST.get('instructions', '')

        # Save to session for OTP confirmation
        request.session['order_data'] = {
            'product_id': product.id,
            'quantity': qty,
            'address': address,
            'payment_method': payment,
            'instructions': instructions,
        }

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        request.session['otp'] = otp
        messages.info(request, f"Test OTP: {otp}")  # Show for testing

        return redirect('verify_otp')

    return render(request, 'shop/place_order.html', {'product': product})


@login_required
def track_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'shop/track_orders.html', {'orders': orders})

def order_success(request):
    return render(request, 'shop/order_success.html')

def track_view_page(request):
  if request.user.is_authenticated:
    orders=Order.objects.filter(user=request.user)
    return render(request,"shop/track_orders.html",{'orders':orders})
  else:
    return redirect("/")
  
def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.none()
    
    return render(request, 'shop/search_results.html', {'products': products, 'query': query})

@login_required
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        real_otp = request.session.get('otp')

        if user_otp == real_otp:
            order_data = request.session.get('order_data')
            if order_data:
                product = Product.objects.get(id=order_data['product_id'])
                quantity = int(order_data['quantity'])
                total = quantity * product.selling_price

                # Create order
                Order.objects.create(
                    user=request.user,
                    product=product,
                    quantity=quantity,
                    address=order_data['address'],
                    total_price=total
                )
                # Clear session
                del request.session['otp']
                del request.session['order_data']

                messages.success(request, "Order placed successfully!")
                return redirect('order_success')
            else:
                messages.error(request, "Order session expired.")
                return redirect('cart')
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'shop/verify_otp.html')

def send_otp(request):
    otp = generate_otp()
    request.session['otp'] = otp
    messages.info(request, f"Your OTP is: {otp}")
    return redirect('verify_otp')






    