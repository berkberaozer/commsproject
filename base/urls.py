from django.urls import path, include
from . import views

app_name = "base"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginPage.as_view(), name="login"),
    path("get_messages", views.GetMessages.as_view(), name="get_messages"),
    path("send_message", views.SendMessage.as_view(), name="send_message"),
    path("search_user", views.SearchUser.as_view(), name="search_user"),
    path("create_chat", views.CreateChat.as_view(), name="create_chat"),
]
