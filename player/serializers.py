from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):

    mobile = serializers.CharField()


class SendOTPSerializer(serializers.Serializer):

    mobile = serializers.CharField()

from player.models import PlayerQueue


class SendOTPSerializer(serializers.Serializer):

    mobile = serializers.CharField()


class PlayerQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerQueue
        fields = '__all__'

