from django.urls import path
from .views import (
    UserPostItemView,
    update_profile
)

app_name = 'user'

urlpatterns = [
    path('<str:username>/', UserPostItemView.as_view(), name='profile'),
    path('<str:username>/edit/', update_profile, name='edit-profile')
]
