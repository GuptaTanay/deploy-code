from game.models import Category, Game
from player.models import PlayerQueue, Player

from celery import task



@task

def poll_queue():
    categories = Category.objects.all()
    for category in categories:
        q = PlayerQueue.objects.filter(category=category)[:2]
        print(q.values())
        if len(q) == 2:
            Game.objects.create(playerA=Player.objects.get(id=q[0].player_id), playerB=Player.objects.get(id=q[1].player_id), category=category)
            PlayerQueue.objects.filter(id__in=q.values('id')).delete()
