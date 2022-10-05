from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse


def notification(request):

    if request.method != 'POST':
        return HttpResponseBadRequest

    print(request.POST)
    
    # body = {
    #     "address"   : "bc1qkfcwrwva3s82j3m4uyv7zvvsgqk9kc36ggykw2", 
    #     "status"    : "3742b7c6e559d347734a4c4cdd40fded22458fd6b43f9a2f78d61a990c5ca712"},

    return HttpResponse('hihih')