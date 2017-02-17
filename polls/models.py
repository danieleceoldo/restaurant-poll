#
# project: restaurant-poll
# author: Daniele Ceoldo
# 
#
#
# This file is part of restaurant-poll.
#
# restaurant-poll is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# restauran-poll is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with restaurant-poll.  If not, see <http://www.gnu.org/licenses/>.
#



from django.db import models


class Ballot(models.Model):
    date = models.DateField('ballot date')
    winner = models.CharField(max_length=30, default="")
    win_cause = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.date.__str__()


class Restaurant(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.name 


class Ranking(models.Model):
    restaurant = models.CharField(max_length=30, default="")
    lwsma_feedback = models.DecimalField(max_digits=6, decimal_places=2,
            default=0)

    def __str__(self):
        return self.restaurant


class Feedback(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0)
    comment = models.CharField(max_length=1024, default="")

