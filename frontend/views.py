from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import login, logout


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ctx['otp_sent'] = self.otp_sent()
        ctx['player_id'] = self.request.GET.get("playerId")
        ctx['wrong'] = self.wrong()
        return ctx

    def otp_sent(self):
        return "otpsent" in self.request.GET.keys()

    def post(self, request, *args, **kwargs):
        if "action" in self.request.POST.keys():
            if self.request.POST.get("action") == "verify-otp":
                from player.models import OTP
                from player.models import Player
                player = Player.objects.get(id=self.request.POST.get("player"))
                otp = OTP.verify(self.request.POST.get("otp"),
                                 player)
                if otp:
                    player.active = True
                    player.save()
                    login(self.request, player.user, backend='django.contrib.auth.backends.ModelBackend')

                else:
                    return HttpResponseRedirect("/?otpsent=1&wrong=1&playerId=" + str(player.id))

                if not player.username:
                    return HttpResponseRedirect("/username?playerId=" + str(player.id))
                return HttpResponseRedirect("/categories/")

    def wrong(self):
        return "wrong" in self.request.GET.keys()
    
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_anonymous:
            return HttpResponseRedirect('/categories')
        return super(HomeView, self).get(request, *args, **kwargs)


class CategoriesView(LoginRequiredMixin, TemplateView):
    template_name = "categories.html"

    def get_context_data(self, **kwargs):
        ctx = super(CategoriesView, self).get_context_data(**kwargs)
        ctx['categories'] = self.get_categories()
        ctx['domains'] = self.get_domains()
        return ctx

    def get_categories(self):
        from game.models import Category
        return Category.objects.all()

    def get_domains(self):
        from game.models import Domain
        return Domain.objects.all()


class UsernameView(LoginRequiredMixin, TemplateView):
    template_name = "username.html"

    def get_context_data(self, **kwargs):
        ctx = super(UsernameView, self).get_context_data(**kwargs)
        ctx['unavailable'] = self.unavailable()
        ctx['player'] = self.player()
        return ctx

    def post(self, request, *args, **kwargs):
        from player.models import Player

        check = Player.objects.filter(username=self.request.GET.get("player")).first()
        if check is not None:
            return HttpResponseRedirect("/categories?unavailable")

        player = Player.objects.get(id=self.request.POST.get("player"))
        player.username = self.request.POST.get("username")
        player.save()
        return HttpResponseRedirect("/categories")

    def unavailable(self):
        return "unavailable" in self.request.GET.keys()

    def player(self):
        return self.request.GET.get("playerId")


class GameView(LoginRequiredMixin, TemplateView):
    template_name = "game.html"

    def get(self, request, *args, **kwargs):
        game = self.get_game()
        player = self.get_player()
        if game.asked_questions.all().count() == 10:
            game.completed = True
            game.save()
            return HttpResponseRedirect("/game/end/" + str(game.id) + "/" + str(player.id) + "/")
        return super(GameView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(GameView, self).get_context_data(**kwargs)
        ctx['question'] = self.get_question()
        ctx['game'] = self.get_game()
        ctx['player'] = self.get_player()
        print(ctx)
        return ctx

    def get_question(self):
        from game.models import Game
        game = Game.objects.get(id=self.kwargs.get("game"))
        return game.get_random_question()

    def get_game(self):
        from game.models import Game
        return Game.objects.get(id=self.kwargs.get("game"))

    def get_player(self):
        from player.models import Player
        return Player.objects.get(id=self.kwargs.get("player"))

    def post(self, request, *args, **kwargs):
        if "action" in self.request.POST.keys():
            if self.request.POST.get("action") == "submit-answer":
                from game.models import Question

                question = Question.objects.get(id=self.request.POST.get("question"))
                choice = question.choices.get(id=self.request.POST.get("choice"))
                player = self.get_player()
                game = self.get_game()
                game.record_answer(player=player, choice=choice, question=question)

                if choice.correct:
                    return HttpResponseRedirect(self.request.path + "?unicorns=love")
                return HttpResponseRedirect(self.request.path + "?zombies=kill")

    def last_correct(self):
        return "unicorns" in self.request.GET.keys()

    def last_wrong(self):
        return "zombies" in self.request.GET.keys()


class GameEndView(LoginRequiredMixin, TemplateView):
    template_name = "gameend.html"

    def get_game(self):
        from game.models import Game
        return Game.objects.get(id=self.kwargs.get("game"))

    def get_player(self):
        from player.models import Player
        return Player.objects.get(id=self.kwargs.get("player"))

    def get_context_data(self, **kwargs):
        from player.models import Player
        from game.models import Game
        ctx = super(GameEndView, self).get_context_data(**kwargs)
        ctx['leaderboard'] = self.get_leaderboard()
        ctx['game'] = self.get_game()

        if ctx['game'].playerA == Player.objects.get(id = self.kwargs.get('player')):
            ctx['resources'] = ctx['game'].player_a_resource
        else:
            ctx['resources'] = ctx['game'].player_b_resource
        return ctx

    def get_leaderboard(self):
        return self.get_game().category.get_leaderboard()


class MatchMaking(TemplateView):
    template_name = 'matchmaking.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MatchMaking,self).get_context_data(*args, **kwargs)
        context['category'] = self.request.GET.get('category')
        context['mode'] = self.request.GET.get('mode')
        return context


class LogOutView(View):

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        self.request.user.player.active = False
        logout(self.request)
        return HttpResponseRedirect("/")

