#views.py file for loading pages in the django project. 
#from django.http import HttpResponse
from django.shortcuts import render

def homepage(request):
    #return HttpResponse("Welcome to the homepage!")
    return render(request, 'home.html') #this line renders the homepage.html template when the homepage view is accessed.
def about(request):
    #return HttpResponse("This is the about page.")
     return render(request, 'about.html')

