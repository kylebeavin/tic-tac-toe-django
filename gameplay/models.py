from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.core.validators import  MaxValueValidator, MinValueValidator

GAME_STATUS_CHOICES = (
    ('F', 'First Player To Move'),
    ('S', 'Second Player To Move'),
    ('W', 'First Player Wins'),
    ('L', 'Second Player Wins'),
    ('D', 'Draw')
)

class GamesQuerySet(models.QuerySet):
    def games_for_user(self, user):

        return self.filter(
            Q(first_player=user) | Q(second_player=user)
        )

    def active(self):
        return self.filter(
            Q(status='F') | Q(status='S')
        )

class Game(models.Model):
    first_player = models.ForeignKey(User,
                                     related_name="games_first_player", on_delete=models.CASCADE)
    second_player = models.ForeignKey(User,
                                      related_name="games_second_player", on_delete=models.CASCADE)

    start_time = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, default='F',
                              choices=GAME_STATUS_CHOICES)

    objects = GamesQuerySet.as_manager()

    def board(self):
        """Return a 2-dimensional list of Move objects,
        so you can ask for the state of a square at position [y][x]."""
        board = [[None for x in range(3)] for y in range(3)]
        for move in self.move_set.all():
            board[move.y][move.x] = move
        return board

    def is_users_move(self, user):
        return (user==self.first_player and self.status == 'F') or\
                (user == self.second_player and self.status == 'S')

    def new_move(self):
        """Returns  a new move object with player, game, and count preset"""
        if self.status not in 'FS':
            raise ValueError("Cannot make move on finished game")

        return Move(
            game=self,
            by_first_player=self.status == 'F'
        )

    def get_absolute_url(self):
        return reverse('gameplay_detail', args=[self.id])

    def __str__(self):
        return "{0} vs {1}".format(
            self.first_player, self.second_player)

class Move(models.Model):
    x = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(3-1)]
    )
    y = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(3-1)]
    )
    comment = models.CharField(max_length=300, blank=True)
    by_first_player = models.BooleanField(editable=False)
    game = models.ForeignKey(Game,editable=False, on_delete=models.CASCADE)
