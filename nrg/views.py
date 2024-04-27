from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from .forms import *
from django.db import connection
from django.db.models import Avg  # Import Avg for aggregation


def index(request):
    reviews = Review.objects.all().order_by('-id') # Sorting by highest to lowest ID
    context = {
        "reviews": reviews
    }
    return render(request, "nrg/index.html" ,context)


def brand_detail(request, brand_id):
    # Fetch brand
    brand = Brand.objects.raw('SELECT * FROM nrg_brand WHERE id = %s', [brand_id])[0]

    # Fetch drinks of the brand
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * 
        FROM nrg_drink 
        WHERE brand_id = %s
    ''', [brand_id])
    drinks = cursor.fetchall()

    # Calculate average ratings for each drink
    drink_ratings = []

    for drink in drinks:
        cursor.execute('''
            SELECT AVG(energy_rating) AS avg_energy_rating, AVG(flavor_rating) AS avg_flavor_rating
            FROM nrg_review
            WHERE drink_id = %s
        ''', [drink[0]])
        avg_ratings = cursor.fetchone()
        drink_ratings.append({
            'drink_id': drink[0],
            'avg_energy_rating': avg_ratings[0],
            'avg_flavor_rating': avg_ratings[1]
        })

    cursor.close()

    print(drink_ratings)

    return render(request, 'nrg/brand_detail.html',
                  {'brand': brand, 'drinks': drinks, 'drink_ratings': drink_ratings})


def register_drink(request):
    if request.method == 'POST':
        form = DrinkRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page after registering the drink
    else:
        form = DrinkRegistrationForm()
    return render(request, 'nrg/register_drink.html', {'form': form})


def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page after creating the review
    else:
        form = ReviewForm()
    return render(request, 'nrg/create_review.html', {'form': form})


def update_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if request.method == 'POST':
        energy_rating = request.POST.get('energy_rating')
        flavor_rating = request.POST.get('flavor_rating')

        # Check if ratings are within the valid range
        if not (0 <= int(energy_rating) <= 10) or not (0 <= int(flavor_rating) <= 10):
            return HttpResponseBadRequest("Energy and flavor ratings must be between 0 and 10.")

        review.energy_rating = energy_rating
        review.flavor_rating = flavor_rating
        review.save()

        return redirect('index')  # Redirect to the index page after updating

    return render(request, 'nrg/update_review.html', {'review': review})


def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM nrg_review WHERE id = %s", [review_id])

        return redirect('index')  # Redirect to the index page after deleting

    return render(request, 'nrg/delete_review.html', {'review': review})


def average_reviews(request):
# Define default values for min and max if not provided
    default_min = 0
    default_max = 10

    # Fetch filter values from GET parameters with defaults
    min_energy = request.GET.get('min_energy', str(default_min))  # Default to 0
    max_energy = request.GET.get('max_energy', str(default_max))  # Default to 10
    min_flavor = request.GET.get('min_flavor', str(default_min))
    max_flavor = request.GET.get('max_flavor', str(default_max))

    # Convert string inputs to float safely
    try:
        min_energy = float(min_energy)
    except ValueError:
        min_energy = default_min

    try:
        max_energy = float(max_energy)
    except ValueError:
        max_energy = default_max

    try:
        min_flavor = float(min_flavor)
    except ValueError:
        min_flavor = default_min

    try:
        max_flavor = float(max_flavor)
    except ValueError:
        max_flavor = default_max

    # Retrieve all drinks and calculate their average ratings
    drinks = Drink.objects.all()
    drinks_with_ratings = []

    for drink in drinks:
        # Get related reviews for the drink and calculate averages
        reviews = Review.objects.filter(drink=drink)

        if reviews.exists():
            avg_energy = reviews.aggregate(Avg('energy_rating'))['energy_rating__avg']
            avg_flavor = reviews.aggregate(Avg('flavor_rating'))['flavor_rating__avg']

            # Apply filters based on min and max average energy and flavor ratings
            if (min_energy <= avg_energy <= max_energy) and \
               (min_flavor <= avg_flavor <= max_flavor):
                drinks_with_ratings.append({
                    'drink': drink,
                    'avg_energy': avg_energy,
                    'avg_flavor': avg_flavor
                })
        else:
            drinks_with_ratings.append({
                'drink': drink,
                'avg_energy': None,
                'avg_flavor': None
            })

    return render(request, 'nrg/average_reviews.html', {'drinks_with_ratings': drinks_with_ratings})