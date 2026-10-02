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
from django.urls import path, include
from . import views #imports the views.py file from the current directory (appProto)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage), #this line maps the root URL to the homepage view function in views.py
    path('about/', views.about), #this line maps the 'about/' URL to the about view function in views.py
    path('products/', include('products.urls'))
]


#REMEMBER CTRL+s to save changes to file. This url patterns lets users access the admin page of the django project.
#We will add more urls to this list as we create more views and pages for our project. 