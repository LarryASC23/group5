from django.urls import path
from . import views #imports the views.py file from the current directory

urlpatterns = [
    path('', views.products), #this line maps the root URL to the products view function in views.py

]


#REMEMBER CTRL+s to save changes to file. This url patterns lets users access the admin page of the django project.
#We will add more urls to this list as we create more views and pages for our project. 