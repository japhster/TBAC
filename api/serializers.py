from rest_framework import serializers

from tbac import models


class GameNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)


class AddExitSerializer(serializers.Serializer):
    room_2 = serializers.PrimaryKeyRelatedField(
        queryset=models.Room.objects.all(),
    )
    leave_room_1 = serializers.CharField(required=False, allow_blank=True)
    leave_room_2 = serializers.CharField(required=False, allow_blank=True)
    is_locked = serializers.BooleanField(required=False, allow_null=True)
    key_required = serializers.PrimaryKeyRelatedField(
        queryset=models.Item.objects.filter(item_type=models.Item.ItemTypeChoices.KEY),
        allow_null=True,
        required=False,
    )

    def validate(self, *args, **kwargs):
        validated_data = super().validate(*args, **kwargs)
        if (
            validated_data.get("is_locked", False)
            and validated_data.get("key_required") is None
        ):
            raise serializers.ValidationError(
                {
                    "key_required": "You need to select a key when the connection is locked."
                }
            )

        return validated_data


class AttackSerializer(serializers.Serializer):
    attack_pk = serializers.IntegerField()
    enemy = serializers.PrimaryKeyRelatedField(queryset=models.Enemy.objects.all())
