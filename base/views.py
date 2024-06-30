from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages     # send error messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required     # decorator to restrict pages
from django.db.models import Q      # to filter more than 1 condition
from django.urls import reverse
# from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


# rooms = [
#   {'id':1, 'name':"Let's learn python!"},
#   {'id':2, 'name':"Design with me."},
#   {'id':3, 'name':"Frontend Developers"},
# ]



def loginPage(request):
  page = 'login'
  # user already logged in, when goes to login url
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == "POST":
    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
      user = User.objects.get(email=email)

    except:
      messages.error(request, "User doesn't exist")

    user = authenticate(request, email=email, password=password)

    if user is not None:
      login(request, user=user)       # creates a session in db & browser
      return redirect('home')
    else:
      messages.error(request, "Incorrect Password")

  context = {'page': page}
  return render(request, 'base/login_register.html', context)



def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)   # just to lowercase (commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
  logout(request)
  return redirect('home')



def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
  )
  topics = Topic.objects.all()[:5]   # display only 5 topics
  room_count = rooms.count()
  room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))   # see only activities that you filter

  context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
  return render(request, 'base/home.html', context)



def room(request, pk):
  room = Room.objects.get(id=pk)
  room_messages = room.message_set.all().order_by('-created')   # get all message of a room -> parent-model.lower-case-child-model_{get-all-attributes}
  participants = room.participants.all()

  if request.method == "POST":
    message = Message.objects.create(
      user=request.user,
      room=room,
      body=request.POST.get('body')
    )
    # TODO: if user already present
    room.participants.add(request.user)
    return redirect('room', pk=room.id)     # go back to the room with the get request
  
  context = {'room': room, 'room_messages': room_messages, 'participants': participants}
  return render(request, 'base/room.html', context)



def userProfile(request, pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  topics = Topic.objects.all()
  context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
  return render(request, 'base/profile.html', context)



@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)    # model form defined in forms.py
  if request.method == "POST":
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', pk=user.id)
  return render(request, 'base/update-user.html', {'form': form})



@login_required(login_url='login')
def createRoom(request):
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    # handle newly created topic ; check if topic already present
    topic, created = Topic.objects.get_or_create(name=topic_name)
    Room.objects.create(
      host=request.user,
      topic=topic,
      name=request.POST.get('name'),
      description=request.POST.get('description'),
    )
    # form = RoomForm(request.POST)
    # if form.is_valid():
    #   room = form.save(commit=False)
    #   room.host = request.user
    #   room.save()
    return redirect('home')
    
  context = {'form': form, 'topics': topics}
  return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def updateRoom(request, pk):
  # print(dir(Room.objects))
  # print(help(Room.objects.get))
  room = Room.objects.get(id=pk)
  topics = Topic.objects.all()
  # get prefilled form
  form = RoomForm(instance=room)

  if request.user != room.host:
    return HttpResponse('You are not alllowed here!!')

  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    # to handle newly created topic during edit
    topic, created = Topic.objects.get_or_create(name=topic_name)
    # form = RoomForm(request.POST, instance=room)
    # if form.is_valid():
    #   form.save()
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('home')
    
  context = {'form': form, 'topics': topics, 'room': room}
  return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.user != room.host:
    return HttpResponse('You are not alllowed here!!')

  if request.method == 'POST':
    room.delete()
    return redirect('home')
  context = {'obj':room}
  return render(request, 'base/delete.html', context)



@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if request.user != message.user:
    return HttpResponse('You are not alllowed here!!')

  # TODO: Redirect back to same room.
  if request.method == 'POST':
    message.delete()
    return redirect(reverse('room', args=[message.room.id]))
  
  context = {'obj': message}
  return render(request, 'base/delete.html', context)



def topicsPage(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  topics = Topic.objects.filter(name__icontains=q)
  return render(request, 'base/topics.html', {'topics': topics})



def activitiesPage(request):
  room_messages = Message.objects.all()
  return render(request, 'base/activity.html', {'room_messages': room_messages})