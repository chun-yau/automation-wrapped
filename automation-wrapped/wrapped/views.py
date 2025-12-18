from django.shortcuts import render

def wrapped(request):

    context = {}
    return render(request, "wrapped/wrapped.html", context)