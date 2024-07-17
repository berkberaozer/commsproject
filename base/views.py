from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.files.storage import default_storage
from django.db.models import Q
from django.core.files.base import File

import io

from commsproject.settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from .forms import RegistrationForm
from mimetypes import guess_extension

from .models import Chat


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
        pass_phrase = get_random_string(length=255)
        if form.is_valid():
            form = form.cleaned_data
            get_user_model().objects.create_user(username=form['username'], email=form['email'],
                                                 password=form['password'],
                                                 first_name=form['first_name'],
                                                 last_name=form['last_name'], pass_phrase=pass_phrase)

            return render(request, self.template_name, {'form': form, 'register': True, 'pass_phrase': pass_phrase, 'username': form['username'], 'email': form['email']})
        else:
            return render(request, self.template_name, {'form': form})


class IndexView(LoginRequiredMixin, View):
    login_url = '../auth/login/'

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        chats = Chat.objects.filter(users=self.request.user)

        return render(context={'chats': chats, 'DATA_UPLOAD_MAX_MEMORY_SIZE': DATA_UPLOAD_MAX_MEMORY_SIZE},
                      request=self.request, template_name="base/index.html")


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
        if request.POST.getlist('users[]'):
            chat = Chat.objects.create()

            for user in request.POST.getlist('users[]'):
                chat.users.add(get_user_model().objects.get(username=user))
            chat.users.add(request.user)

            if request.POST.get('name'):
                chat.name = request.POST.get('name')
            chat.save()

            return JsonResponse({"chat_id": chat.id, "success": True})
        else:
            print(request.POST.get('users'))
            return JsonResponse({"success": False})


class UploadFile(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        date = timezone.now()
        file = File(file=io.BytesIO(request.body),
                    name=request.user.username + "-" + str(date.timestamp()) + guess_extension(self.request.content_type))
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)

        return JsonResponse({"message": file_url, "fileName": self.request.headers.get("name")})


class PassPhrase(LoginRequiredMixin, View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        return JsonResponse({"passPhrase": get_user_model().objects.get(id=self.request.user.id).pass_phrase})


class PublicKey(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=self.request.user.id)
        user.public_key = request.POST.get('public_key')
        user.save()

        return JsonResponse({"success": True})
