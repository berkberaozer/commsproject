from django.urls import path
from base import views

app_name = "base"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginPage.as_view(), name="login"),
    path("logout", views.LogoutPage.as_view(), name="logout"),
    path("search_user", views.SearchUser.as_view(), name="search_user"),
    path("create_chat", views.CreateChat.as_view(), name="create_chat"),
    path("upload", views.UploadFile.as_view(), name="upload"),
    path("set_credentials", views.SetCredentials.as_view(), name="set_credentials"),
    path("get_public_key", views.GetPublicKey.as_view(), name="get_public_key"),
]
