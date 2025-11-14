from django.http import HttpResponseRedirect
from django.urls import path

def root_redirect(request):
    return HttpResponseRedirect('/admin/')

urlpatterns = [
    path('', root_redirect, name='root'),
]
