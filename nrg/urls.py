from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('brand/<int:brand_id>/', views.brand_detail, name='brand_detail'),
    path('review/<int:review_id>/update/', views.update_review, name='update_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('create-review/', views.create_review, name='create_review'),
    path('register-drink/', views.register_drink, name='register_drink'),
    path('average-reviews/', views.average_reviews, name='average_reviews'),
]