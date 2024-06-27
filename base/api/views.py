# from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer
from base.models import Room

@api_view(['GET'])
def getRoutes(request):
  routes = [
    'GET /api',
    'GET /api/rooms',
    'GET /api/rooms/:id'
  ]
  # return JsonResponse(routes, safe=False)    # JsonResponse converts to json data
  return Response(routes)


@api_view(['GET'])
def getRooms(request):
  rooms = Room.objects.all()   # type -> python list of objects ; should be serialized
  serializer = RoomSerializer(rooms, many=True)
  return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
  rooms = Room.objects.get(id=pk)   # type -> python list of objects ; should be serialized
  serializer = RoomSerializer(rooms, many=False)
  return Response(serializer.data)