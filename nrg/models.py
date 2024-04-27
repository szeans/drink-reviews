from django.db import models

# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Drink(models.Model):
    CHOICES = {
        0: "None",
        1: "Low",
        2: "Medium",
        3: "High"
    }

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE) #foreign key to brand
    name = models.CharField(max_length=50)
    caffeine = models.IntegerField(choices=CHOICES)
    sugar = models.IntegerField(choices=CHOICES)

    def __str__(self):
        return self.name


class Review(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE) #foreign key to drink
    energy_rating = models.PositiveIntegerField(default=0) #from 1-10
    flavor_rating = models.PositiveIntegerField(default=0) #from 1-10