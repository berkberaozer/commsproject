from django.contrib import messages
import json
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.views import (View, generic)
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from datetime import datetime
from .forms import RegistrationForm
from django.db.models import Q

from .models import User, Chat, Message


# Create your views here.

class LoginPage(LoginView):
    def post(self, request, *args, **kwargs):
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

        if user:
            login(request, user)
            messages.success(request, 'You are now logged in!')
            return HttpResponseRedirect(reverse("base:index"))

    def get(self, request, *args, **kwargs):
        return render(request, template_name="base/index.html")


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = RegistrationForm
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'],
                                            first_name=form.cleaned_data['first_name'],
                                            last_name=form.cleaned_data['last_name'])
            User.save(user)
            print(User.objects.values())

            return HttpResponseRedirect(reverse('base:index'))
        else:
            return render(request, self.template_name, {'form': form})


class IndexView(LoginRequiredMixin, View):
    login_url = '../auth/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        data = {}
        if 'search' in self.request.GET and self.request.GET['search']:
            data['users'] = User.objects.filter(username__contains=self.request.GET['search'])
        if 'talk' in self.request.GET and self.request.GET['talk'] and User.objects.filter(
                username=self.request.GET['talk']).exists():
            data['talk'] = User.objects.filter(username__contains=self.request.GET['talk'])
        data['user_chats'] = Chat.objects.filter(belong=self.request.user)
        data['chat_messages'] = Message.objects.filter(Q(source=request.user.id) | Q(target=request.user.id))
        return HttpResponse(render(context=data, request=self.request, template_name="base/index.html"))

    def post(self, request, *args, **kwargs):
        if 'message' in self.request.POST:
            send_to = self.request.POST['talk']
            Message.objects.create(user=User.objects.get(username=send_to), message=request.POST['message'],
                                   date=datetime.now())
            Chat.objects.filter(belong=self.request.user, target__username=send_to)

        return HttpResponseRedirect(reverse('base:index'))


class GetMessages(View):

    def get(self, request, *args, **kwargs):
        chat_id = self.request.GET.get('chat')
        queryset = Message.objects.filter(chat=chat_id).values()
        return JsonResponse({"messages": list(queryset)})
