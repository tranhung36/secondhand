from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CheckoutForm, CouponForm
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon

# stripe
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(View):

    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order.")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                # lấy giá trị từ hàm nhập form
                phone_number = form.cleaned_data.get('phone_number')
                city = form.cleaned_data.get('city')
                district = form.cleaned_data.get('district')
                street_address = form.cleaned_data.get('street_address')
                payment_option = form.cleaned_data.get('payment_option')
                # tạo billing address
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
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect('core:cart')


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
            }
            return render(self.request, 'payment.html', context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            # phương thức charge trong stripe
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )
            # Tạo thanh toán
            payment = Payment()
            # lấy id stripe
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # cập nhật số lượng sản phẩm người dùng đã đặt mua theo đơn hàng
            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()

            # Chỉ định thanh toán cho đơn hàng
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")
        # mẫu xử lý lỗi trong stripe
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.warning(
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
                'couponform': CouponForm()
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
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
    # hàm get or create nhận vào 1 tuple,
    # nếu orderitem rỗng thì sẽ nhận biến created, ngược lại order_item,
    # lọc theo sản phẩm, người dùng, đơn chưa xử lý
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # kiểm tra nếu sản phẩm trong đơn hàng có tồn tại
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
    # lọc đơn hàng thông qua user, đơn hàng chưa đặt
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # kiểm tra nếu sản phẩm trong đơn hàng có tồn tại
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.warning(request, "This item was removed from your cart.")
        else:
            messages.warning(request, "This item was not in your cart.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(request, "You do not have an active order.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # lọc đơn hàng thông qua user, đơn hàng chưa đặt
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # kiểm tra nếu sản phẩm trong đơn hàng có tồn tại
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
            messages.warning(request, "This item was not in your cart.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(request, "You do not have an active order.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddCouponView(View):
    def post(self, *args, **kwargs):
        now = timezone.now()
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                coupon_qs = Coupon.objects.filter(
                    code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
                order_coupon = Order.objects.filter(
                    coupon=coupon_qs.first(), user=self.request.user)
                if order_coupon:
                    messages.warning(
                        self.request, "You can't use same coupon again")
                    return redirect('core:cart')
                if coupon_qs:
                    order.coupon = coupon_qs[0]
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                    return redirect('core:cart')
                else:
                    messages.error(self.request, "Coupon doesn not exists")
                    return redirect('core:cart')

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order.")
                return redirect('core:cart')
