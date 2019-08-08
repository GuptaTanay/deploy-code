from django.db import models

from django.db.models import Q
from django.contrib.auth.models import User


class OTP(models.Model):

    otp = models.CharField(max_length=220)
    player = models.ForeignKey("player.Player", on_delete=models.SET_NULL, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    #expired = models.BooleanField(default=False)

    @classmethod
    def create(cls, player):
        import random, string
        otp = ''.join(random.choice(string.digits) for _ in range(4))
        return cls.objects.create(
            otp=otp,
            player=player
        )

    @classmethod
    def verify(cls, otp, player):
        import datetime
        otp = cls.objects.filter(otp=otp, player=player, created_on__gte=datetime.datetime.now() - datetime.timedelta(minutes=2)).first()
        # if otp:
        #     otp.expired = True
        #     otp.save()

        return True if otp else False


class Player(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    username = models.TextField()
    mobile = models.TextField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.username


    def score_in_category(self, category):
        from game.models import Game, Category

        game = Game.objects.filter(Q(playerA=self) | Q(playerB=self)).filter(category=category)

        score = [g.total_score[0 if g.playerA == self else 1] for g in game]
        return sum(score)


class PlayerQueue(models.Model):
    from game.models import Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    player = models.OneToOneField(Player, on_delete=models.SET_NULL, null=True )

