from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request, 'store/home.html')

from .models import Branch

def find_nearby_branches(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    results = []

    if lat and lon:
        lat = float(lat)
        lon = float(lon)

        branches = Branch.objects.all()
        for b in branches:
            dist = haversine(lon, lat, b.longitude, b.latitude)
            results.append({
                'branch': b,
                'distance': dist,
            })
        
        results.sort(key=lambda x: x['distance'])

    return render(request, 'store/nearby.html', {'results': results})
from .models import Stock, Product, Branch, Cart

def select_branch(request, branch_id):
    branch = Branch.objects.get(id=branch_id)

    # ผูก Cart กับสาขาที่เลือก
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.branch = branch
        cart.save()

    return redirect('product_by_branch', branch_id=branch.id)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})

import math

def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # รัศมีโลก (กิโลเมตร)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def product_by_branch(request, branch_id):
    branch = Branch.objects.get(id=branch_id)
    stocks = Stock.objects.filter(branch=branch).select_related('product')

    return render(request, 'store/product_list.html', {
        'branch': branch,
        'stocks': stocks,
    })

from .models import CartItem

def add_to_cart(request, branch_id, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)
    branch = Branch.objects.get(id=branch_id)
    qty = int(request.POST.get('quantity', 1))

    # ตรวจสต็อกก่อน
    stock = Stock.objects.get(branch=branch, product=product)
    if qty > stock.quantity:
        return redirect('product_by_branch', branch_id=branch_id)

    # สร้างหรืออ่านตะกร้า
    cart, created = Cart.objects.get_or_create(user=request.user, branch=branch)

    # เพิ่มรายการ
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = qty
    item.save()

    return redirect('cart')

def cart_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart = Cart.objects.filter(user=request.user).first()
    
    items_with_total = []
    if cart:
        for item in cart.items.select_related('product'):
            total = item.quantity * item.product.price
            items_with_total.append({
                'id': item.id,
                'name': item.product.name,
                'qty': item.quantity,
                'price': item.product.price,
                'total': total,
            })

    return render(request, 'store/cart.html', {
        'items': items_with_total
    })

def update_cart_item(request, item_id):
    if request.method == "POST":
        qty = int(request.POST.get("quantity"))
        item = CartItem.objects.get(id=item_id)

        # เช็กสต็อก
        stock = Stock.objects.get(branch=item.cart.branch, product=item.product)
        if qty <= stock.quantity:
            item.quantity = qty
            item.save()

    return redirect("cart")

def delete_cart_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.delete()
    return redirect("cart")

from .models import Order, OrderItem

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cart')

    items = cart.items.select_related("product")

    # แปลง items ให้เป็น dict เพื่อส่งไป template (ป้องกันปัญหา mul filter)
    items_list = []
    for item in items:
        items_list.append({
            "id": item.id,
            "name": item.product.name,
            "qty": item.quantity,
            "price": item.product.price,
            "total": item.quantity * item.product.price,
        })

    total_price = sum([i["total"] for i in items_list])

    # เมื่อกดปุ่มยืนยันคำสั่งซื้อ
    if request.method == "POST":
        # สร้างออเดอร์หลัก
        order = Order.objects.create(
            user=request.user,
            branch=cart.branch,
            total_price=total_price,
        )

        # บันทึกรายการสินค้าในออเดอร์
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            # ลดจำนวน stock ของสาขานั้น
            stock = Stock.objects.get(branch=cart.branch, product=item.product)
            stock.quantity -= item.quantity
            stock.save()

        # เคลียร์ตะกร้า
        cart.items.all().delete()

        return redirect("order_success", order_id=order.id)

    return render(request, "store/checkout.html", {
        "items": items_list,
        "total_price": total_price,
    })

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "store/order_success.html", {"order": order})

def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "store/my_orders.html", {
        "orders": orders
    })

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(id=order_id, user=request.user)
    items = order.items.select_related("product")

    return render(request, "store/order_detail.html", {
        "order": order,
        "items": items
    })







