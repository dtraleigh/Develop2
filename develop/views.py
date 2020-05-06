from django.shortcuts import render


def cac(request):
    return render(request, 'index.html')
