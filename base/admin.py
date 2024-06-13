from django.contrib import admin
from .models import Person, Chat, Message

# Register your models here.

admin.site.register(Person)
admin.site.register(Chat)
admin.site.register(Message)
