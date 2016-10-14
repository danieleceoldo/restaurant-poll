from django.db import models

# Create your models here.

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

    def __str__(self):
        return self.restaurant


class Feedback(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0)
    comment = models.CharField(max_length=1024, default="")

