from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.response import Response

from player import serializers

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response

from player import serializers
from player.models import Player, PlayerQueue
from player.serializers import PlayerQueueSerializer

from django.contrib.auth.models import User


class SendOTPView(GenericAPIView):

    serializer_class = serializers.SendOTPSerializer

    def post(self, request, *args, **kwargs):

        from comms.message91 import Message91
        from player.models import Player
        player, created = Player.objects.get_or_create(
            mobile=request.data.get("mobile")
        )

        if not player.user:
            import uuid
            player.user = User.objects.create(
                username=request.data.get("mobile"),
                password=str(uuid.uuid4())
            )
            player.save()

        msg91 = Message91()
        msg91.send_otp("+91", to=[player.mobile], player=player)

        return Response({
            "status": "success",
            "message": "OTP was sent!",
            "created": created,
            "playerId": player.id

        })


class VerifyOTPView(GenericAPIView):

    def post(self, request, *args, **kwargs):

        from player.models import Player, OTP
        otp = request.data.get("otp")
        player = Player.objects.filter(mobile=request.data.get("mobile")).first()
        verified = OTP.verify(otp, player)

        return Response({
            "verified": verified
        })


class UpdatePlayerName(GenericAPIView):
    def post(self, request, *args, **kwargs):
        from player.models import Player
        mobile = request.data.get("mobile")
        name = request.data.get("name")
        player = Player.objects.filter(mobile=mobile).first()
        player.username = name
        player.save()

        return Response({
            "change": "Name Successful"
        })


class AddToQueueAPI(CreateAPIView):
    serializer_class = PlayerQueueSerializer


class DeleteFromQueue(GenericAPIView):
    serializer_class = PlayerQueueSerializer

    def post(self, request, *args, **kwargs):
        player = request.data.get('player')
        print(player)
        PlayerQueue.objects.filter(player=player).delete()
        return Response(player)
