from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze, name='analyze'),
    path('history/', views.history, name='history'),
    path('result/<int:analysis_id>/', views.result, name='result'),
]