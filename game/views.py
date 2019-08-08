# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from game.serializers import GameSerializer
from game import models
from rest_framework.response import Response
from django.db.models import Q
from player.models import Player
from game.models import Game, Question


class MatchFoundAPI(APIView):

    def get(self, request, *args, **kwargs):
            game = models.Game.objects.filter(Q(playerA=Player.objects.get(id=request.GET.get('player')))
                                              | Q(playerB=Player.objects.get(id=request.GET.get('player'))),
                                              completed=False).first()
            if game:
                data = GameSerializer(game).data
                print(data)
                data['found'] = True
                return Response(data)
            else:
                return Response({'found': False})


class CreateGameAPI(CreateAPIView):
    serializer_class = GameSerializer


class CheckGameAPI(GenericAPIView):
    serializer_class = GameSerializer

    def post(self, request, *args, **kwargs):
        game = self.request.data.get("game")
        player = self.request.data.get("player")
        question = self.request.data.get("question")

        gameref = Game.objects.get(id=game)
        playerref = Player.objects.get(id=player)
        questionref = Question.objects.get(id=question)

        gameref.timeout(playerref, questionref)

        return Response({
            "Sent": "Data Sent"
        })
