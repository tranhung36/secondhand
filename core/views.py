from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CheckoutForm
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress, Payment

# stripe
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                phone_number = form.cleaned_data.get('phone_number')
                city = form.cleaned_data.get('city')
                district = form.cleaned_data.get('district')
                street_address = form.cleaned_data.get('street_address')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    phone_number=phone_number,
                    street_address=street_address,
                    city=city,
                    district=district
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('core:cart')


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order,
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )
            # Tạo thanh toán
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # Chỉ định thanh toán cho đơn hàng
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")


class HomeView(ListView):
    model = Item
    template_name = 'index.html'


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class ShopView(ListView):
    model = Item
    template_name = 'shop.html'
    paginate_by = '12'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'detail.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.warning(request, "This item was removed from your cart.")
        else:
            # add a message saying the order doesn't contain the item
            messages.warning(request, "This item was not in your cart.")
            HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # add a message saying the user doesn't have an order
        messages.warning(request, "You do not have an active order.")
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.warning(request, "This item quantity was updated.")
        else:
            # add a message saying the order doesn't contain the item
            messages.warning(request, "This item was not in your cart.")
            HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # add a message saying the user doesn't have an order
        messages.warning(request, "You do not have an active order.")
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
