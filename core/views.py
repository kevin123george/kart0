from django.shortcuts import render, get_object_or_404, redirect
from .models import Item,\
    OrderItem,\
    Order,\
    Address,\
    Payment,\
    UserProfile,\
    Coupon,\
    Refund
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm

import random
import string
import stripe

stripe.api_key = 'sk_test_YvRLxFpoheL9o83dVzvHJUKP00TXosKCun'

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def home(request):
    context = {
        'items': Item.objects.all().order_by('-created_on')
    }
    return render(request, "index.html", context)

class CategoryListView(ListView):
    model = Item
    template_name = 'categorylist.html'

    def get_queryset(self):

        category = self.kwargs.get('category')
        
        print (category)
        return Item.objects.filter(category=category).order_by('-created_on')



class ItemDetailView(DetailView):
    model = Item
    template_name = 'single-product-details.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            context = {
                'object': order,

            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:

            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("order-summary")


    else:

        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)

        messages.info(request, "This item was added to your cart.")
        return redirect("product-detail", slug=item.slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.quantity = 1
            order_item.save()
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product-detail", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product-detail", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]

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
            messages.info(request, "The item quantity was updated")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product-detail", slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect("product-detail", slug=slug)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order,
                'form': form,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )

            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, 'checkout.html', context)

        except ObjectDoesNotExist:
            messages.info(self.request, "you don not have an active order")
            return redirect("check-out")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('check-out')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('check-out')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'C':
                    
     
                    order_items = order.items.all()


                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()



                    order.ordered = True

                    order.ref_code = create_ref_code()
                    order.save()

                    messages.success(self.request, "Your order was successful!")
                    return redirect("/")
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('check-out')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order-summary")

class PaymentMethod(View):
    def get(self, *args, **kwargs):

        order = Order.objects.get(user=self.request.user, ordered=False)
        print("Billing = ", order.billing_address)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, 'payment.html', context)
        else:
            messages.error(
                self.request, "You have not added a billing address")
            return redirect("check-out")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total() * 100)
        token = self.request.POST.get('stripeToken')


        try:
            charge = stripe.Charge.create(

                amount=amount,
                currency="usd",
                source=token,  
            )


            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()


            order_items.update(ordered=True)
            for item in order_items:
                item.save()



            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:

            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:

            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:

            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:

            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:

            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:

            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("payment/stripe")


def product(request):
    return render(request, 'product-page.html')


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                coupon_qs = Coupon.objects.filter(code=code)

                if coupon_qs:
                    order.coupon = coupon_qs[0]
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                    return redirect("check-out")
                else:
                    messages.success(self.request, "Coupon Does not Exists")
                    return redirect("check-out")

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("check-out")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        ref_code = self.kwargs.get('ref_code')

        initial_data = {
            'ref_code': ref_code

        }
        form = RefundForm(initial=initial_data)
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        ref_code = self.kwargs.get('ref_code')
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email

                messages.info(self.request, "your messages was received")
                return redirect("profile")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exists")
                return redirect("request-refund", ref_code=ref_code)

class ProfileView(View):
    def get(self, *args, **kwargs):

        orders = Order.objects.filter(
            user=self.request.user, ordered=True)

        context = {
            "orders": orders,


        }
        return render(self.request, "profilepage.html", context)




def board_index(request):
    projects = Item.objects.all()
    lookup = request.GET.get('q')
    print (lookup)
    if lookup:
            projects = Item.objects.filter(Q(title__icontains = lookup) | Q(category__icontains = lookup) |Q(description__icontains = lookup) )
    context = {
        'projects': projects
    }
    return render(request, 'exp.html', context)
