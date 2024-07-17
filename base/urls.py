from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginPage.as_view(), name="login"),
    path("search_user", views.SearchUser.as_view(), name="search_user"),
    path("create_chat", views.CreateChat.as_view(), name="create_chat"),
    path("upload", views.UploadFile.as_view(), name="upload"),
    path("pass_phrase", views.PassPhrase.as_view(), name="pass_phrase"),
    path("public_key", views.PublicKey.as_view(), name="public_key"),
]
