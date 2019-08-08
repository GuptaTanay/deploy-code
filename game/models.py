from django.db import models
from model_utils import Choices


class Domain(models.Model):

    domain = models.CharField(max_length=220)


class Category(models.Model):

    category = models.CharField(max_length=220)
    domain = models.ForeignKey("game.Domain", on_delete=models.SET_NULL, null=True)

    description = models.TextField(default="This is the description of the category")

    def __str__(self):
        return self.category

    class Meta(object):
        verbose_name_plural = "Categories"

    def get_top_players(self):
        from player.models import Player
        from game.models import Game

        games = Game.objects.filter(category=self, completed=True)
        if games.count() < 1:
            return []
        return sorted([(g.total_score, g) for g in games], key=lambda tup: tup[0], reverse=True)[:3]

    def get_leaderboard(self):
        from player.models import Player
        scores = [(p.score_in_category(self), p) for p in Player.objects.all()]
        return sorted(scores, key=lambda tup: tup[0], reverse=True)


class Resource(models.Model):
    title = models.CharField(max_length=30)
    url = models.URLField()
    category = models.ForeignKey("game.Category", on_delete= models.SET_NULL, null=True)
    difficulty = Choices('Beginner','Intermediate','Expert')
    level = models.CharField(choices=difficulty, default=difficulty.Beginner, max_length=20)

    def __str__(self):
        return self.title


class Question(models.Model):

    question = models.TextField()
    category = models.ForeignKey("game.Category", on_delete=models.SET_NULL, null=True)

    choices = models.ManyToManyField("game.Choice")

    def __str__(self):
        return self.question

    @property
    def difficulty(self):
        # TODO: Change this later.
        return 1


class Choice(models.Model):

    choice = models.TextField()
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice


class Game(models.Model):

    playerA = models.ForeignKey("player.Player", on_delete=models.SET_NULL, null=True, related_name="playerA+")
    playerB = models.ForeignKey("player.Player", on_delete=models.SET_NULL, null=True, related_name="playerB+")

    category = models.ForeignKey("game.Category", on_delete=models.SET_NULL, null=True)
    asked_questions = models.ManyToManyField("game.Question", related_name="asked_question+", blank=True)

    answers = models.ManyToManyField("game.Answer", blank=True)
    completed = models.BooleanField(default=False)

    @property
    def total_score(self):
        return sum([a.score for a in self.answers.filter(player=self.playerA)]), sum(
            [a.score for a in self.answers.filter(player=self.playerB)])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.playerA == self.playerB:
            raise StandardError("Are you nuts?")

        if self.playerB and self.playerA:
            if not any([self.playerA.active, self.playerB.active]):
                raise StandardError("All players are not active. -_-")

        return super(Game, self).save(force_insert=False, force_update=False, using=None,
                                      update_fields=None)

    def get_random_question(self):
        return Question.objects.filter(category=self.category).exclude(id__in=[i.id for i in self.asked_questions.all()]).order_by("?").first()

    def record_answer(self, player=None, question=None, choice=None):
        answer = Answer.objects.create(
            question=question,
            choice=choice,
            player=player
        )
        self.answers.add(answer)
        self.asked_questions.add(question)
        self.save()

    def timeout(self, player=None, question=None):
        a = question.choices.all().values()
        b = 0
        for x in a:
            if not x['correct']:
                b = x['id']

        choice = question.choices.get(id=b)

        answer = Answer.objects.create(
            question=question,
            choice=choice,
            player=player
        )
        self.answers.add(answer)
        self.asked_questions.add(question)
        self.save()



    @property
    def winner(self):
        if not self.playerB:
            return self.playerA

        player_a_scores = sum([_.score for _ in self.answers.filter(player=self.playerA, choice__correct=True)])
        player_b_scores = sum([_.score for _ in self.answers.filter(player=self.playerB, choice__correct=True)])
        return self.playerA if player_a_scores > player_b_scores else self.playerB

    @property
    def number_of_questions_asked(self):
        return self.asked_questions.all().count() + 1

    @property
    def player_a_score(self):
        return sum([x.score for x in self.answers.filter(player=self.playerA)])

    @property
    def player_b_score(self):
        return sum([x.score for x in self.answers.filter(player=self.playerB)])

    @property
    def player_a_correct_answers(self):
        return self.answers.filter(player=self.playerA, choice__correct=True).count()

    @property
    def player_b_correct_answers(self):
        return self.answers.filter(player=self.playerB, choice__correct=True).count()

    @property
    def player_a_resource(self):
        if self.player_a_score <= 20:
            return Resource.objects.filter(category=self.category, level='Beginner').order_by('?')[:3]
        elif 20 < self.player_a_score <= 50:
            return Resource.objects.filter(category=self.category, level='Intermediate').order_by('?')[:3]
        else:
            return Resource.objects.filter(category=self.category, level='Expert').order_by('?')[:3]
    @property
    def player_b_resource(self):
        if self.player_b_score <= 20:
            return Resource.objects.filter(category=self.category, level='Beginner').order_by('?')[:3]
        elif 20 < self.player_b_score <= 50:
            return Resource.objects.filter(category=self.category, level='Intermediate').order_by('?')[:3]
        else:
            return Resource.objects.filter(category=self.category, level='Expert').order_by('?')[:3]


class Answer(models.Model):

    question = models.ForeignKey("game.Question", on_delete=models.SET_NULL, null=True)
    choice = models.ForeignKey("game.Choice", on_delete=models.SET_NULL, null=True)
    player = models.ForeignKey("player.Player", on_delete=models.SET_NULL, null=True)

    @property
    def score(self):
        if self.choice.correct:
            return 10
        return 0