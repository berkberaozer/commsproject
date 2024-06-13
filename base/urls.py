from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginPage.as_view(), name="login"),
    path("get_messages", views.GetMessages.as_view(), name="get_messages"),
    path("send_message", views.SendMessage.as_view(), name="send_message"),
]