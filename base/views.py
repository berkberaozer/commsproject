from typing import Any

from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .forms import RegistrationForm


from .models import User, Chat, Message


# Create your views here.

class LoginPage(LoginView):
    def post(self, request):
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

        if user:
            login(request, user)
            messages.success(request, 'You are now logged in!')
            return HttpResponseRedirect(reverse("base:index"))


    def get(self, request):
        return render(request)




class RegisterView(generic.FormView):
    template_name = 'registration/register.html'

    def get(self, request):
        form = RegistrationForm
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'],first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'])
            User.save(user)
            print(User.objects.values())

            return HttpResponseRedirect(reverse('base:index'))
        else:
            return render(request, self.template_name, {'form': form})

class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '../auth/login/'
    redirect_field_name = ''
    template_name = "base/index.html"
    context_object_name = "active_chats"

    def get_queryset(self):
        return Chat.objects.filter(belong__id=self.request.user.id)
