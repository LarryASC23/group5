from django.urls import path
from . import views #imports the views.py file from the current directory

app_name = "products"

urlpatterns = [
    path('', views.products, name='list'), # product catalog

]


#REMEMBER CTRL+s to save changes to file. This url patterns lets users access the admin page of the django project.
#We will add more urls to this list as we create more views and pages for our project. 
