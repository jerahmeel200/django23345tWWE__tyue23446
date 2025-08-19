from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
import requests
from cart.models import Cart


@login_required
def payment_process(request):
    cart = getattr(request.user, 'cart', None)

    if not cart or not cart.items.exists():
        return render(request, 'payments/payment_process.html', {
            'error': "Your cart is empty."
        })

    total_amount = int(cart.total_price() * 100)  # Paystack wants amount in kobo

    if request.method == 'POST':
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        callback_url = request.build_absolute_uri(reverse('payment_callback'))
        #   add callback_url
        data = {
            'email': request.user.email or "guest@example.com",
            'amount': total_amount,
            'callback_url': callback_url,
        }

        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=headers,
            json=data
        )
        res_data = response.json()

        if res_data.get('status'):
            return redirect(res_data['data']['authorization_url'])
        else:
            return render(request, 'payments/payment_failed.html', {
                'error': res_data.get('message')
            })

    return render(request, 'payments/payment_process.html', {
        'cart': cart,
        'items': cart.items.all(),
        'total_amount': cart.total_price(),  # in naira for display
    })


@login_required
def payment_callback(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, "Payment could not be verified.")
        return redirect('product_list')

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get('status') and res_data['data']['status'] == 'success':
        #   Payment successful → clear cart
        cart = getattr(request.user, 'cart', None)
        if cart:
            cart.items.all().delete()

        messages.success(request, "Payment successful! 🎉")
        return redirect('product_list')
    else:
        messages.error(request, "Payment failed or was not completed.")
        return redirect('view_cart')
