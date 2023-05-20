from django.urls import path
from srmapp.views import detect_drowsiness

urlpatterns = [
    path('detect_drowsiness/', detect_drowsiness, name='detect_drowsiness'),
]
