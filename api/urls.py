from django.urls import path, include

from api.views import CreateReviewView, DeleteReviewView, ListUserReviewView, DetailReviewView, ListReviewView, \
    DetailUserView

urlpatterns = [
    path('create-review', CreateReviewView.as_view(), name='create-review'),
    path('delete-review/<int:pk>', DeleteReviewView.as_view(), name='delete-review'),
    path('list-reviews', ListReviewView.as_view(), name='list-reviews'),
    path('get-review/<int:pk>', DetailReviewView.as_view(), name='get-review'),
    path('list-user-reviews', ListUserReviewView.as_view(), name='get-user-reviews'),
    path('user-info', DetailUserView.as_view(), name='user-info'),
]
