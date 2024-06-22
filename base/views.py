from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages     # send error messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required     # decorator to restrict pages
from django.db.models import Q      # to filter more than 1 condition

from .models import Room, Topic, Message
from .forms import RoomForm


# rooms = [
#   {'id':1, 'name':"Let's learn python!"},
#   {'id':2, 'name':"Design with me."},
#   {'id':3, 'name':"Frontend Developers"},
# ]


# login logic
def loginPage(request):

  # user already logged in, when goes to login url
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
      user = User.objects.get(username=username)
    except:
      messages.error(request, "User does not exist")

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user=user)       # creates a session in db & browser
      return redirect('home')
    else:
      messages.error(request, "Username OR Password does not exist")

  context = {}
  return render(request, 'base/login_register.html', context)


# logout and redirect back to home page
def logoutUser(request):
  logout(request)
  return redirect('home')


# all functionalities in home page
def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
  )
  topics = Topic.objects.all()
  room_count = rooms.count()
  context = {'rooms':rooms, 'topics':topics, 'room_count':room_count}
  return render(request, 'base/home.html', context)


# Inside each room ; using room id
def room(request, pk):
  room = Room.objects.get(id=pk)
  room_messages = room.message_set.all().order_by('-created')   # get all message of a room -> parent-model.lower-case-child-model_{get-all-attributes}
  
  if request.method == "POST":
    message = Message.objects.create(
      user=request.user,
      room=request.room,
      body=request.POST.get('body')
    )
    return redirect('room', pk=room.id)     # go back to the room with the get request
  
  context = {'room': room, 'room_messages': room_messages}
  return render(request, 'base/room.html', context)


# To create new room
@login_required(login_url='login')
def createRoom(request):
  form = RoomForm()
  if request.method == 'POST':
    # print(request.POST)
    form = RoomForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('home')
    
  context = {'form':form}
  return render(request, 'base/room_form.html', context)


# edit existing room ; 
@login_required(login_url='login')
def updateRoom(request, pk):
  # print(dir(Room.objects))
  # print(help(Room.objects.get))
  room = Room.objects.get(id=pk)
  # get prefilled form
  form = RoomForm(instance=room)

  if request.user != room.host:
    return HttpResponse('You are not alllowed here!!')

  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room)
    if form.is_valid():
      form.save()
      return redirect('home')
    
  context = {'form':form}
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