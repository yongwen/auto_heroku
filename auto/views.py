# Create your views here.
from django.shortcuts import render_to_response
import os

def home(request):
    return render_to_response('index.html', {})

def work(request):

    os.system("git")
    return render_to_response('work.html', {})