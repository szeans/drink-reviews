# forms.py

from django import forms
from .models import *


class DrinkRegistrationForm(forms.ModelForm):
    class Meta:
        model = Drink
        fields = ['brand', 'name', 'caffeine', 'sugar']


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['drink'].queryset = Drink.objects.all()

        # Customize the choices to display both name and brand
        self.fields['drink'].widget = forms.Select(choices=[(drink.id, f"{drink.name} - {drink.brand}") for drink in Drink.objects.all()])

    class Meta:
        model = Review
        fields = ['drink', 'energy_rating', 'flavor_rating']

    def clean_energy_rating(self):
        energy_rating = self.cleaned_data.get('energy_rating')
        if energy_rating < 0 or energy_rating > 10:
            raise forms.ValidationError("Energy rating must be between 0 and 10.")
        return energy_rating

    def clean_flavor_rating(self):
        flavor_rating = self.cleaned_data.get('flavor_rating')
        if flavor_rating < 0 or flavor_rating > 10:
            raise forms.ValidationError("Flavor rating must be between 0 and 10.")
        return flavor_rating

