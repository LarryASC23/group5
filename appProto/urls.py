"""
URL configuration for appProto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts import views as account_views
from cart import views as cart_views
from orders import views as order_views
from . import views #imports the views.py file from the current directory (appProto)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage), #this line maps the root URL to the homepage view function in views.py
    path('about/', views.about), #this line maps the 'about/' URL to the about view function in views.py
    path('products/', include('products.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', account_views.signup, name='signup'),
    path('account/', account_views.account, name='account'),
    path('account/orders/', account_views.order_history, name='order_history'),
    path('account/orders/<int:pk>/', account_views.order_detail, name='order_detail'),
    path('account/password/', auth_views.PasswordChangeView.as_view(success_url='/account/password/done/'), name='password_change'),
    path('account/password/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('cart/add/<int:pk>/', cart_views.add, name='cart_add'),
    path('cart/update/<int:pk>/', cart_views.update, name='cart_update'),
    path('cart/remove/<int:pk>/', cart_views.remove, name='cart_remove'),
    path('checkout/', order_views.checkout, name='checkout'),
    path('checkout/complete/<int:pk>/', order_views.complete, name='checkout_complete'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
