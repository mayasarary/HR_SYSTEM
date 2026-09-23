from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def base_test(request):
        return render(request, 'base.html')

@login_required
def login_view(request):
    return render(request, 'registration/login.html')