from django.urls import path
from .views import (
    PostListView,
    PostDetailView
)

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='blog'),
    path('post/<str:slug>/', PostDetailView.as_view(), name='post')
]
