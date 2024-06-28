from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View
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
        chats = Chat.objects.filter(Q(belong=self.request.user) | Q(target=self.request.user))
        data = {'user_chats': chats,
                'chat_messages': Message.objects.filter(chat__in=chats)}
        return HttpResponse(render(context=data, request=self.request, template_name="base/index.html"))


class GetMessages(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        chat_id = self.request.GET.get('chat')
        queryset = Message.objects.filter(chat=chat_id).order_by('date').values()
        queryset.update(hasReached=True)
        return JsonResponse({"messages": list(queryset)})


class SendMessage(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        chat_id = request.POST.get('chat_id')
        Message.objects.create(source=User.objects.get(id=request.POST.get("source_id")),
                               target=Chat.objects.get(id=chat_id).target, message=request.POST.get("message"),
                               date=datetime.now(), chat=Chat.objects.get(id=chat_id))
        try:
            Message.objects.create(source=User.objects.get(id=request.POST.get("source_id")),
                                   message=request.POST.get("message"),
                                   date=datetime.now(),
                                   chat=Chat.objects.get(belong=Chat.objects.get(id=chat_id).target,
                                                         target=Chat.objects.get(id=chat_id).belong))

        except ObjectDoesNotExist:
            Chat.objects.create(belong=Chat.objects.get(id=chat_id).target,
                                target=User.objects.get(id=request.POST.get("source_id")))
            Message.objects.create(source=User.objects.get(id=request.POST.get("source_id")),
                                   target=Chat.objects.get(id=chat_id).target, message=request.POST.get("message"),
                                   date=datetime.now(),
                                   chat=Chat.objects.get(belong=Chat.objects.get(id=chat_id).target,
                                                         target=Chat.objects.get(id=chat_id).belong))
        return JsonResponse({"success": True})


class SearchUser(View):
    def get(self, request, *args, **kwargs):
        searched_username = request.GET.get('username')
        users = User.objects.filter(
            Q(username__contains=searched_username) & ~Q(username=self.request.user.username)).values('first_name',
                                                                                                      'last_name', 'id',
                                                                                                      'username')
        return JsonResponse({"users": list(users)})


class CreateChat(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('target'):
            target = User.objects.get(username=request.POST.get('target'))
            belong = self.request.user
            chat = Chat.objects.create(belong=belong, target=target)

            return JsonResponse({"chat_id": chat.id})
        else:
            return JsonResponse({"success": False})


class ReadMessage(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('id'):
            message = Message.objects.get(id=request.POST.get('id'))
            message.hasRead = True
            message.save()
            return JsonResponse({"success": True})


class ReachedMessage(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('id'):
            message = Message.objects.get(id=request.POST.get('id'))
            message.hasReached = True
            message.save()
            return JsonResponse({"success": True})
