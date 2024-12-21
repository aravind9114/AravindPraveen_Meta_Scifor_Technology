from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('fitness-form/', views.fitness_view, name='fitness_form'), 
    path('fitness/result/', views.fitness_view, name='fitness_result'),
    path('fitness-history/', views.fitness_history, name='fitness_history'),

]
