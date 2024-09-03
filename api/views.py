from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Review
from api.serializers import ReviewSerializer, UserSerializer


# Create your views here.
class CreateReviewView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    model = Review

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DeleteReviewView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    model = Review

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)


class ListReviewView(ListAPIView):
    authentication_classes = []
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-date_posted']


class ListUserReviewView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-date_posted']

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)


class DetailUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DetailReviewView(RetrieveAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = []

    def get_queryset(self):
        return Review.objects.filter(id=self.kwargs['pk'])



