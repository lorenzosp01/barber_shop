import jwt
from django.contrib.auth.models import User
from jose.constants import ALGORITHMS
import boto3
from dotenv import load_dotenv
from rest_framework.authentication import BaseAuthentication, get_authorization_header
import hmac, hashlib, base64
import os
from jwt.algorithms import RSAAlgorithm
from rest_framework.exceptions import AuthenticationFailed

load_dotenv()

client_secret = os.getenv('COGNITO_CLIENT_SECRET')
client_id = os.getenv('COGNITO_CLIENT_ID')


def get_secret_hash(username):
    message = bytes(username + client_id, 'utf-8')
    key = bytes(client_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash


def login(username, password):
    secret_hash = get_secret_hash(username)
    response = None

    client = boto3.client('cognito-idp', region_name='eu-west-3')

    try:
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash,
            },
            ClientId=client_id,
        )
    except client.exceptions.NotAuthorizedException as e:
        pass

    return response


class CognitoAuthenticationBackend(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        public_key = RSAAlgorithm.from_jwk(os.getenv('COGNITO_JWK'))
        try:
            decoded = jwt.decode(auth[1].decode(), public_key,  algorithms=["RS256"])
            # Get the sub (subject) claim from the ID token
            try:
                user = User.objects.get(
                    username=decoded['sub'],
                )
            except User.DoesNotExist:
                raise AuthenticationFailed('No such user')

            return user, auth
        except IndexError:
            raise AuthenticationFailed('No token provided')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')



