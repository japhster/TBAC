from rest_framework import serializers


class GameNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)