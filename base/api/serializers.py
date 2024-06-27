# serializers -> Classes that take certain models we want to seralize & turn it into JSON data/object.

from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
  class Meta:
    model = Room
    fields = '__all__'