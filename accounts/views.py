from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from orders.models import Order
from .forms import ProfileForm, SignUpForm


def signup(request):
    form = SignUpForm(request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created.")
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
            return redirect(next_url)
        return redirect("account")
    return render(request, "registration/signup.html", {"form": form, "next": next_url})


@login_required
def account(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("account")
    return render(request, "account/account.html", {"form": form})


@login_required
def order_history(request):
    orders = request.user.orders.select_related("discount_code").prefetch_related("items").order_by("-created_at")
    return render(request, "account/orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.filter(user=request.user).select_related("discount_code").prefetch_related("items__product"),
        pk=pk,
    )
    return render(request, "account/order_detail.html", {"order": order})
