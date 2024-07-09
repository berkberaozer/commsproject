from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.files.storage import default_storage

from .forms import RegistrationForm
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
import base64
from django.core.files.base import ContentFile, File
import io
from mimetypes import guess_extension
from django.core import serializers

from .models import Chat, Message


# Create your views here.

class LoginPage(LoginView):
    def post(self, request, *args, **kwargs):
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

        if user:  # if user is authenticated
            login(request, user)

            return HttpResponseRedirect(reverse("base:index"))

    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="base/index.html")


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = RegistrationForm
        return render(request, self.template_name, {'form': form})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form = form.cleaned_data
            get_user_model().objects.create_user(username=form['username'], email=form['email'],
                                                 password=form['password'],
                                                 first_name=form['first_name'],
                                                 last_name=form['last_name'])

            return render(request, self.template_name, {'form': form, 'register': True})
        else:
            return render(request, self.template_name, {'form': form})


class IndexView(LoginRequiredMixin, View):
    login_url = '../auth/login/'

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        chats = Chat.objects.filter(Q(belong=self.request.user) | Q(target=self.request.user))

        return render(context={'chats': chats}, request=self.request, template_name="base/index.html")


class SearchUser(LoginRequiredMixin, View):  # case-insensitive user search, request user is excluded
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        searched_username = request.GET.get('username')

        users = get_user_model().objects.filter(Q(username__icontains=searched_username) &
                                                ~Q(username=self.request.user.username)).values('first_name',
                                                                                                'last_name', 'id',
                                                                                                'username')

        return JsonResponse({"users": list(users)})


class CreateChat(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.POST.get('target'):
            target = get_user_model().objects.get(username=request.POST.get('target'))
            chat = Chat.objects.create(belong=self.request.user, target=target)

            return JsonResponse({"chat_id": chat.id, "success": True})
        else:
            return JsonResponse({"success": False})


class UploadFile(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        date = timezone.now()
        file = File(io.BytesIO(request.body),
                    name=request.user.username + "-" + str(date.timestamp()) + guess_extension(self.request.content_type))
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)

        message = Message.objects.create(source=get_user_model().objects.get(id=request.user.id),
                                         message=file_url, date=date, chat=Chat.objects.get(id=self.request.headers.get("chat")),
                                         isFile=self.request.headers.get("name"))

        return JsonResponse({"success": True, "message": serializers.serialize("json", Message.objects.filter(pk=message.pk))})
