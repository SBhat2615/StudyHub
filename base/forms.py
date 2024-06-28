from django.forms import ModelForm
from .models import Room, User
# from django.contrib.auth.models import User

# inherit UserCreationForm ; if directly used display's all field
# class MyUserCreationForm(UserCreationForm):
#   class Meta:
#     model = User
#     fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
  class Meta:
    model = Room
    fields = '__all__'
    exclude = ['host', 'participants']


class UserForm(ModelForm):
  class Meta:
    model = User
    fields = ['username', 'email']

