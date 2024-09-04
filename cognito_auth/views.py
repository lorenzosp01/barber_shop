import os

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import boto3
import dotenv
from cognito_auth.serializers import CognitoUserSerializer, TokenSerializer
from cognito_auth.utils import login

dotenv.load_dotenv()


# class CognitoAuthenticationMixin(LoginRequiredMixin):
#     def dispatch(self, request, *args, **kwargs):
#         id_token = request.POST.get('id_token')  # Get the ID token from the frontend
#         user = authenticate(request, id_token=id_token)
#         if user:
#             login(request, user)
#             # Redirect or respond accordingly upon successful authentication
#             return HttpResponse('Authenticated')
#         else:
#             # Handle authentication failure
#             return HttpResponse('Authentication failed')

class RefreshTokenView(GenericAPIView):
    authentication_classes = []
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh_token']

        client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))
        response = client.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': login.get_secret_hash(os.getenv('COGNITO_USERNAME')),
            },
            ClientId=os.getenv('COGNITO_CLIENT_ID'),
        )

        token = TokenSerializer(data={
            'access_token': response['AuthenticationResult']['AccessToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken'],
        })

        token.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK, data=token.data)


class LoginView(GenericAPIView):
    authentication_classes = []
    serializer_class = CognitoUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        response = login(username, password)
        if not response:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Invalid credentials'})

        token = TokenSerializer(data={
            'access_token': response['AuthenticationResult']['AccessToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken'],
        })

        token.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK, data=token.data)


class SignupView(GenericAPIView):
    authentication_classes = []
    serializer_class = CognitoUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))
        try:
            response = client.sign_up(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                Username=username,
                Password=password,
                SecretHash=login.get_secret_hash(username),
            )
        except client.exceptions.UsernameExistsException:
            return Response(status=status.HTTP_409_CONFLICT, data={'error': 'Username already exists'})

        return Response(status=status.HTTP_201_CREATED, data=response)


class TestView(APIView):
    authentication_classes = []

    def get(self, request):
        User.objects.get(username='admin')
        return Response(status=status.HTTP_200_OK, data={'message': 'Hello, world!'})
