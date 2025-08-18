from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem

# Helper function to get/create a user's cart
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_user_cart(request.user)

    # check if item already exist in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        # if product already in cart, increase quantity
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')  #rediret to cart pag

@login_required
def view_cart(request):
    cart = get_user_cart(request.user)
    items = cart.items.all() # all cartItems for this cart
    total = cart.total_price()

    return render(request, "cart/cart.html", {"cart": cart, "items": items, "total": total})


@login_required
def remove_from_cart(request, item_id):
    cart = get_user_cart(request.user)
    item = get_object_or_404(CartItem, id= item_id, cart=cart)
    item.delete()
    return redirect("view_cart")

@login_required
def update_cart(request, item_id):
    cart = get_user_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            # if quantity is 0 remove the item
            item.delete()
    return redirect("view_cart")


