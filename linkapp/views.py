import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import AllowAny
from django.contrib.auth.password_validation import validate_password
from .models import UserVerification, GoogleUser
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view

from .serializers import *
from django.db.models import Count, F
from django.db.models import Q



from django.http import JsonResponse
import os
import json
from kmodes.kmodes import KModes

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string
from django.utils.html import strip_tags


from rest_framework import serializers


import numpy as np

from django.contrib.auth import get_user_model

User = get_user_model()  # This can be your regular User model









class EmptySerializer(serializers.Serializer):
    pass

class PasswordResetAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate password reset token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct password reset email
        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"  # Adjust the frontend URL if needed

        subject = "Password Reset Requested"
        email_template_name = "password_reset_email.html"
        context = {
            'reset_link': reset_link,
            'user': user,
        }

        # Render HTML content
        html_content = render_to_string(email_template_name, context)
        # Generate plain text by stripping HTML tags
        text_content = strip_tags(html_content)

        # Create the email
        email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        # Attach the HTML version
        email.attach_alternative(html_content, "text/html")
        # Send email
        email.send()

        return Response({
            "message": "Password reset link has been sent to your email.",
            "token": token,
            "uid": uid
        }, status=status.HTTP_200_OK)




class PasswordResetConfirmAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')

        if not uidb64 or not token or not password:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)








def country_city_region_view(request):
    # Get the directory of the current file (views.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the JSON file
    file_path = os.path.join(current_dir, 'country_city_region.json')
    
    # Open and load the JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse({'error': 'File not found'}, status=404)





class PropertySearchView(APIView):
    def get(self, request):
        # Get optional filters from query parameters
        state = request.query_params.get('state', None)
        country = request.query_params.get('country', None)
        city = request.query_params.get('city', None)
        property_type = request.query_params.get('type', None)

        # Ensure at least one filter is provided
        if not any([state, country, property_type]):
            return Response({"error": "At least one filter (state, country, type) is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Build the query conditions dynamically
        filters = Q()
        if state:
            filters &= Q(state=state)
        if city:
            filters &= Q(city=city)
        if country:
            filters &= Q(country=country)
        if property_type:
            filters &= Q(type=property_type)

        # Query UserProperty and GoogleUserProperty
        user_properties = UserProperty.objects.filter(filters)
        google_user_properties = GoogleUserProperty.objects.filter(filters)

        # Serialize the data
        user_properties_data = UserPropertySerializer(user_properties, many=True).data
        google_user_properties_data = GoogleUserPropertySerializer(google_user_properties, many=True).data

        # Combine both sets of data
        combined_data = {
            'user_properties': user_properties_data,
            'google_user_properties': google_user_properties_data
        }

        return Response(combined_data, status=status.HTTP_200_OK)


class GoogleSinUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        token_id = request.data.get('token_id')

        # Create or update the GoogleUser
        user, created = GoogleUser.objects.get_or_create(
            email=email,
            defaults={'name': name, 'token_id': token_id}
        )

        serializer = GoogleUserSerializer(user)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # New user created
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)  # Existing user

        


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=6))

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Le nom d'utilisateur existe déjà."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "L'email existe déjà."}, status=status.HTTP_400_BAD_REQUEST)
        
   
        try:
            # Validate the password
            validate_password(password)

            # Create user
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

            # Generate and send verification code
            verification_code = self.generate_verification_code()
            UserVerification.objects.create(
                user=user,
                verification_code=verification_code,
                verification_code_expires_at=timezone.now() + timedelta(hours=1)
            )

            # Render email content from HTML template
            subject = 'Your verification code'
            email_template_name = 'verification_email.html'
            context = {
                'user': user,
                'verification_code': verification_code,
            }
            html_content = render_to_string(email_template_name, context)
            plain_message = strip_tags(html_content)  # Fallback for plain text version
            from_email = settings.DEFAULT_FROM_EMAIL

            # Create email with both HTML and plain text parts
            email = EmailMultiAlternatives(subject, plain_message, from_email, [email])
            email.attach_alternative(html_content, "text/html")

            # Send email
            email.send()

            return Response({"message": "User created. Verification email sent."}, status=status.HTTP_201_CREATED)
        except ValidationError as e:

            # Custom French error messages
            errors = []
            for message in e.messages:
                if "This password is too short" in message:
                    errors.append("Ce mot de passe est trop court. Il doit contenir au moins 8 caractères.")
                elif "This password is too common" in message:
                    errors.append("Ce mot de passe est trop commun.")
                elif "This password is entirely numeric" in message:
                    errors.append("Ce mot de passe est entièrement numérique.")
                elif "The password is too similar to the username" in message:
                    errors.append("Le mot de passe est trop similaire au nom d'utilisateur.")
                elif "The password is too similar to the email" in message:
                    errors.append("Le mot de passe est trop similaire à l'adresse e-mail.")
                else:
                    errors.append(message)  # Add any other error without change

            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
         
        except Exception as e:
            return Response({"error": "An error occurred. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        code = data.get('code')

        try:
            verification = UserVerification.objects.get(verification_code=code)
            if verification.verification_code_expires_at > timezone.now():
                user = verification.user
                user.is_active = True  # Assuming you want to activate the user account here
                user.save()
                verification.is_verified = True
                verification.save()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except UserVerification.DoesNotExist:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
        



# CREATE USER PROFILE

# View for creating, listing, retrieving, and updating user profiles
class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
   

    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def perform_create(self, serializer):
        # Get the request user
        user = self.request.user if self.request.user.is_authenticated else None
        # Pass the user to the serializer
        serializer.save(user=user)

# View for retrieving, updating, and deleting a single user profile
class UserUpdateProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users
    
# View for retrieving, updating, and deleting a single user profile
class GoogleUserUpdateProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GoogleUser.objects.all()
    serializer_class = GoogleUserSerializer
  
  
# View for retrieving, updating, and deleting a single user profile
class GoogleMoreUpdateProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GoogleUserProfile.objects.all()
    serializer_class = UserGoogleProfileSerializer


class ImageUserPropertyUpdate(generics.RetrieveUpdateAPIView):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

    permission_classes = [IsAuthenticated]



class ImageGoolgeUserPropertyUpdate(generics.RetrieveUpdateAPIView):
    queryset = GooglePropertyImage.objects.all()
    serializer_class = GooglePropertyImageSerializer


class MyUserProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the currently logged-in user
        user = self.request.user
        
        # Debugging: Print the logged-in user
        print("Logged-in user:", user)
        print("User ID:", user.id)
        
        # Fetch profiles associated with the logged-in user
        queryset = UserProfile.objects.filter(user=user)
        
        # Debugging: Print the resulting queryset
        print("Queryset:", queryset)
        
        return queryset

    def list(self, request, *args, **kwargs):
        # Get the queryset
        queryset = self.get_queryset()
        
        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)
        
        # Return a JSON response
        return Response({
            'actual_user_data': serializer.data,
        })



class UserInterestListCreateView(generics.ListCreateAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
   

    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def perform_create(self, serializer):
        # Get the request user
        user = self.request.user if self.request.user.is_authenticated else None
        # Pass the user to the serializer
        serializer.save(user=user)


class UserPropertyViewSet(viewsets.ModelViewSet):
    queryset = UserProperty.objects.all()
    serializer_class = UserPropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the authenticated user to the 'user' field
        serializer.save(user=self.request.user)


class GoogleUserPropertyViewSet(viewsets.ModelViewSet):
    queryset = GoogleUserProperty.objects.all()
    serializer_class = GoogleUserPropertySerializer
    








class InterestGoogleListCreateView(generics.ListCreateAPIView):
    queryset = InterestGoogle.objects.all()
    serializer_class = InterestGoogleSerializer







class UserGoogleProfileListCreateView(generics.ListCreateAPIView):
    queryset = GoogleUserProfile.objects.all()
    serializer_class = UserGoogleProfileSerializer



class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer





class SpecificGoogleUser(generics.GenericAPIView):

    def get(self, request, id, *args, **kwargs):
        try:
            # Use .get() to retrieve a single object instead of .filter()
            google_user_profile = GoogleUserProfile.objects.get(user=id)

            # Serialize the single object
            google_user_profile_serializer = UserGoogleProfileSerializer(google_user_profile).data

        except GoogleUserProfile.DoesNotExist:
            return Response({'error': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the serialized data.OBJE
        return Response({
            'google_user_profile': google_user_profile_serializer
        })
    




class InterestAlgorithmRecommendationView(generics.GenericAPIView):

    def get_user_interests(self, current_user):
        """Get interests for both regular and Google users."""
        if isinstance(current_user, User):
            return Interest.objects.filter(user=current_user)
        elif isinstance(current_user, GoogleUser):
            return InterestGoogle.objects.filter(user=current_user)
        return None

    def get_all_user_recommendations(self, current_user):
        # Fetch all interests
        all_interests = list(Interest.objects.all()) + list(InterestGoogle.objects.all())
        user_interests = self.get_user_interests(current_user)

        if not user_interests.exists():
            return []

        # Prepare data for clustering
        interest_data = [[interest.name] for interest in all_interests]
        interest_data_array = np.array(interest_data)
        n_clusters = min(5, len(interest_data_array))

        # Perform clustering
        if n_clusters > 1:
            km = KModes(n_clusters=n_clusters, init='Cao', n_init=5, verbose=1)
            clusters = km.fit_predict(interest_data_array)

            # Filter recommendations
            user_recommendations = set()
            for interest in user_interests:
                user_cluster = km.predict([[interest.name]])[0]
                user_recommendations.update(
                    {all_interests[i].user for i, cluster in enumerate(clusters)
                     if cluster == user_cluster and all_interests[i].user != current_user}
                )
            return list(user_recommendations)
        return []

    def get(self, request, *args, **kwargs):
        user_type = kwargs.get('user_type')
        user_id = kwargs.get('user_id')

        # Determine user type and fetch user
        try:
            current_user = User.objects.get(id=user_id) if user_type == 'regular' else GoogleUser.objects.get(id=user_id)
        except (User.DoesNotExist, GoogleUser.DoesNotExist):
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get recommendations
        recommendations = self.get_all_user_recommendations(current_user)
        data = {
            "user_recommendations": [
                {
                    "id": user.id,
                    "username": getattr(user, 'username', None),
                    "google_name": getattr(user, 'name', None)
                }
                for user in recommendations
            ]
        }
        return Response(data)








class SubscribedPropertiesView(generics.GenericAPIView):
    def get(self, request, subscriber_id, subscriber_type, *args, **kwargs):
        # Initialize variables to hold the properties
        user_properties = []
        google_user_properties = []

        # Fetch subscriptions based on the subscriber type
        if subscriber_type == 'regular':
            # If the subscriber is a regular user, find their subscriptions
            subscriptions = Subscription.objects.filter(user=subscriber_id)

            # Loop through subscriptions and get properties
            for sub in subscriptions:
                if sub.subscribed_to_user:
                    user_properties += UserProperty.objects.filter(user=sub.subscribed_to_user)
                if sub.subscribed_to_google_user:
                    google_user_properties += GoogleUserProperty.objects.filter(user=sub.subscribed_to_google_user)

        elif subscriber_type == 'google':
            # If the subscriber is a Google user, find their subscriptions
            subscriptions = Subscription.objects.filter(google_user=subscriber_id)

            # Loop through subscriptions and get properties
            for sub in subscriptions:
                if sub.subscribed_to_user:
                    user_properties += UserProperty.objects.filter(user=sub.subscribed_to_user)
                if sub.subscribed_to_google_user:
                    google_user_properties += GoogleUserProperty.objects.filter(user=sub.subscribed_to_google_user)

        else:
            return Response({'error': 'Invalid subscriber type'}, status=400)

        # Serialize the properties for both regular and Google users
        user_property_serializer = UserPropertySerializer(user_properties, many=True).data
        google_user_property_serializer = GoogleUserPropertySerializer(google_user_properties, many=True).data

        # Return the serialized properties
        return Response({
            'user_properties': user_property_serializer,
            'google_user_properties': google_user_property_serializer
        })



class SpecificProperties(generics.GenericAPIView):

    def get(self, request, state, *args, **kwargs):
        try:
            # Use .filter() to retrieve all matching objects instead of .get()
            user_properties = UserProperty.objects.filter(state=state)
            google_user_properties = GoogleUserProperty.objects.filter(state=state)

            # Initialize empty lists for the response data
            user_property_serializer = []
            google_user_property_serializer = []

            # Serialize the objects if they exist
            if user_properties.exists():
                user_property_serializer = UserPropertySerializer(user_properties, many=True).data
            if google_user_properties.exists():
                google_user_property_serializer = GoogleUserPropertySerializer(google_user_properties, many=True).data

            # If neither model has results, return a 404
            if not user_properties.exists() and not google_user_properties.exists():
                return Response({'error': 'No properties found in either model'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Return a 500 error if something goes wrong
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return the serialized data (either or both)
        return Response({
            'google_user_properties': google_user_property_serializer,
            'user_properties': user_property_serializer
        })


class GoogleUserTokenView(generics.GenericAPIView):


    def get(self, request, email, *args, **kwargs):
        try:
            google_user = GoogleUser.objects.get(email=email)
            google_users_data = GoogleUser.objects.filter(email=email)
          

             # Serialize the data
            serializer = GoogleUserSerializer(google_users_data, many=True)
  
        except GoogleUser.DoesNotExist:
            return Response({'error': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the token_id
        return Response({
            'token_id': google_user.token_id,
            'google_users_data': serializer.data
          
        })
    


class GetUserInfo(generics.GenericAPIView):


    def get(self, request, id, *args, **kwargs):
        try:
            user_data = UserProfile.objects.get(user=id)
            
             # Serialize the data
            serializer = UserProfileSerializer(user_data)
  
        except UserProfile.DoesNotExist:
            return Response({'error': ' user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the user data
        return Response({
            'user_data':serializer.data
            
        })
    



class GetGoogleUserInfo(generics.GenericAPIView):


    def get(self, request, id, *args, **kwargs):
        try:
            google_user_data = GoogleUserProfile.objects.get(user=id)
            more_data = GoogleUser.objects.get(id=id)
            
             # Serialize the data
            serializer_google = UserGoogleProfileSerializer(google_user_data).data
            more_data_serializer = GoogleUserSerializer(more_data).data
            print(f"Fetching data for user with id: {id}")

  
        except GoogleUserProfile.DoesNotExist:
            return Response({'error': f' google user {id} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the user data
        return Response({
            'google_user_data':serializer_google,
            'more_data': more_data_serializer

            
        })
    


class GetPropertiesGoogle(generics.GenericAPIView):

    def get(self, request, id, *args, **kwargs):
        try:
            # Try to fetch the property from UserProperty first
       
            user_property = GoogleUserProperty.objects.filter(user=id)
            property_data_serialized = GoogleUserPropertySerializer(user_property, many=True).data
            return Response({
                    'google_user_property': property_data_serialized,
                })
        except GoogleUserProperty.DoesNotExist:
                # If not found, try to fetch from GoogleUserProperty
                  return Response({'error': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)
 

 

class GetSubscriptionsData(generics.GenericAPIView):

    def get(self, request, id, user_type, *args, **kwargs):
        try:
            if user_type == 'google':
                # Fetch subs for Google user based on the user ID
                google_user = GoogleUser.objects.get(id=id)
                subs = Subscription.objects.filter(google_user=google_user)
            elif user_type == 'regular':
                # Fetch subs for regular user based on the user ID
                regular_user = User.objects.get(id=id)
                subs = Subscription.objects.filter(user=regular_user)
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
            
            if subs.exists():
                sub_data_serialized = SubscriptionSerializer(subs, many=True).data
                return Response({
                    'sub_data': sub_data_serialized,
                })
            else:
                return Response({'message': 'No subs found for this user'}, status=status.HTTP_404_NOT_FOUND)

        except (GoogleUser.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        



class GetLikeGoogle(generics.GenericAPIView):

    def get(self, request, id, user_type, *args, **kwargs):
        try:
            if user_type == 'google':
                # Fetch likes for Google user based on the user ID
                google_user = GoogleUser.objects.get(id=id)
                likes = Like.objects.filter(google_user=google_user)
            elif user_type == 'regular':
                # Fetch likes for regular user based on the user ID
                regular_user = User.objects.get(id=id)
                likes = Like.objects.filter(user=regular_user)
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            if likes.exists():
                like_data_serialized = LikeSerializer(likes, many=True).data
                return Response({
                    'like_data': like_data_serialized,
                })
            else:
                return Response({'message': 'No likes found for this user'}, status=status.HTTP_404_NOT_FOUND)

        except (GoogleUser.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class GetPropertiesUser(generics.GenericAPIView):

    def get(self, request, user, *args, **kwargs):
        try:
            # Try to fetch the property from UserProperty first
       
            user_property = UserProperty.objects.filter(user=user)
            property_data_serialized = UserPropertySerializer(user_property, many=True).data
            return Response({
                    'user_property': property_data_serialized,
                })
        except UserProperty.DoesNotExist:
                # If not found, try to fetch from GoogleUserProperty
                  return Response({'error': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)




class GooglePropsRecommendations(generics.GenericAPIView):

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Fetch all properties for the given user
            user_properties = GoogleUserProperty.objects.filter(user=user_id)

            # Check if there are properties available for the user
            if user_properties.exists():
                # Serialize the queryset
                property_data_serialized = GoogleUserPropertySerializer(user_properties, many=True).data
                return Response({
                    'user_property': property_data_serialized,
                })
            else:
                return Response({'error': 'No properties found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class RegularPropsRecommendations(generics.GenericAPIView):

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Fetch all properties for the given user
            user_properties = UserProperty.objects.filter(user=user_id)

            # Check if there are properties available for the user
            if user_properties.exists():
                # Serialize the queryset
                property_data_serialized = UserPropertySerializer(user_properties, many=True).data
                return Response({
                    'user_property': property_data_serialized,
                })
            else:
                return Response({'error': 'No properties found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSpecificProperties(generics.GenericAPIView):

    def get(self, request, property_id, *args, **kwargs):
        try:
            # Try to fetch the property from UserProperty first
            try:
                user_property = UserProperty.objects.get(property_id=property_id)
                property_data_serialized = UserPropertySerializer(user_property).data
                return Response({
                    'user_property': property_data_serialized,
                    'google_user_property': None,
                })
            except UserProperty.DoesNotExist:
                # If not found, try to fetch from GoogleUserProperty
                google_user_property = GoogleUserProperty.objects.get(property_id=property_id)
                property_google_data_serialized = GoogleUserPropertySerializer(google_user_property).data
                return Response({
                    'user_property': None,
                    'google_user_property': property_google_data_serialized,
                })
        
        except GoogleUserProperty.DoesNotExist:
            # Handle the case where neither model has the property
            return Response({'error': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GoogleAllData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Fetch all properties and related images
            property_data = UserProperty.objects.all().order_by('-created_at')
            property_google_data = GoogleUserProperty.objects.all().order_by('-created_at')
            
            # Serialize the data
            property_data_serialized = UserPropertySerializer(property_data, many=True).data
            property_google_data_serialized = GoogleUserPropertySerializer(property_google_data, many=True).data

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return the data in the response
        return Response({
            'user_properties': property_data_serialized,
            'google_user_properties': property_google_data_serialized,
        })


class GetNameGoogle(generics.GenericAPIView):
     def get(self, request, email, *args, **kwargs):
        try:
            google_user = GoogleUser.objects.get(email=email)
        except GoogleUser.DoesNotExist:
            return Response({'error': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # Serialize the GoogleUserProfile instance
        serializer = GoogleUserSerializer(google_user)
        
        # Return the serialized data
        return Response(serializer.data)
    
    
class GetGoogleUserProfile(generics.GenericAPIView):
    def get(self, request, email, *args, **kwargs):
        try:
            google_user = GoogleUser.objects.get(email=email)
            # my_token_id = google_user.token_id 
            # google_user_profile = GoogleUserProfile.objects.get(token_id=my_token_id)
            google_user_id = google_user.id 
            google_user_profile = GoogleUserProfile.objects.get(user_id=google_user_id)
        except GoogleUser.DoesNotExist:
            return Response({'error': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
        except GoogleUserProfile.DoesNotExist:
            return Response({'error': 'Google user profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the GoogleUserProfile instance
        serializer = UserGoogleProfileSerializer(google_user_profile)
        
        # Return the serialized data
        return Response(serializer.data)
    


class GetUserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the UserProfile instance
        serializer = UserProfileSerializer(user_profile)
        
        # Return the serialized data
        return Response(serializer.data)
    


# GET GOOGLE USER INTEREST CLASS

class GetGoogleUserInterest(generics.GenericAPIView):
    def get(self, request, email, *args, **kwargs):
        try:
            google_user = GoogleUser.objects.get(email=email)
            my_user_id = google_user.id 
            google_user_profile = InterestGoogle.objects.get(user=my_user_id)
        except GoogleUser.DoesNotExist:
            return Response({'error': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
        except InterestGoogle.DoesNotExist:
            return Response({'error': 'Google user  interest not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the GoogleUserProfile instance
        serializer = InterestGoogleSerializer(google_user_profile)
        
        # Return the serialized data
        return Response(serializer.data)


# GET USER INTEREST CLASS


class GetUserInterest(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            user_interest = Interest.objects.get(user=user)
        except Interest.DoesNotExist:
            return Response({'error': 'User interest not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the UserProfile instance
        serializer = InterestSerializer(user_interest)
        
        # Return the serialized data
        return Response(serializer.data)


    



@api_view(['POST'])
def like_property(request, property_id, property_type, user_type):
    user = request.user
    google_user = None
    regular_user = None

    user_id = request.data.get('user_id')

    # Determine whether the user is a regular user or a Google user
    if user_type == 'google':
        try:
            google_user = GoogleUser.objects.get(id=user_id)
        except GoogleUser.DoesNotExist:
            return Response({'message': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            regular_user = User.objects.get(id=user.id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Determine whether the property is a regular property or a Google property
    if property_type == 'google':
        try:
            property_obj = GoogleUserProperty.objects.get(id=property_id)
        except GoogleUserProperty.DoesNotExist:
            return Response({'message': 'Google property not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            property_obj = UserProperty.objects.get(id=property_id)
        except UserProperty.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the like exists for this user and property
    like_exists = Like.objects.filter(
        user=regular_user,
        google_user=google_user,
        property=property_obj if property_type == 'regular' else None,
        google_property=property_obj if property_type == 'google' else None,
        user_type=user_type,
        property_type=property_type
    ).exists()

    if like_exists:
        # Unlike the property
        Like.objects.filter(
            user=regular_user,
            google_user=google_user,
            property=property_obj if property_type == 'regular' else None,
            google_property=property_obj if property_type == 'google' else None,
            user_type=user_type,
            property_type=property_type
        ).delete()
        like_count = Like.objects.filter(
        property=property_obj if property_type == 'regular' else None,
        google_property=property_obj if property_type == 'google' else None,
        property_type=property_type
    ).count()
        return Response({'message': 'unliked',  'like_count': like_count}, status=status.HTTP_200_OK)
    else:
        # Like the property
        Like.objects.create(
            user=regular_user,
            google_user=google_user,
            property=property_obj if property_type == 'regular' else None,
            google_property=property_obj if property_type == 'google' else None,
            user_type=user_type,
            property_type=property_type
        )

 # Calculate the updated like count
    like_count = Like.objects.filter(
        property=property_obj if property_type == 'regular' else None,
        google_property=property_obj if property_type == 'google' else None,
        property_type=property_type
    ).count()
    return Response({
         'message': 'liked',
         'like_count': like_count
        }, status=status.HTTP_201_CREATED)




@api_view(['POST'])
def subscribe_to_user(request, user_id, user_type):
    # Get the authenticated user (from token or session)
    subscriber_id = request.data.get('subscriber_id')  # Expect the subscribing user's ID from the request body
    subscriber_type = request.data.get('subscriber_type')  # Whether the subscribing user is 'regular' or 'google'

    # Initialize variables to hold the subscriber (regular or Google) and the target subscription
    subscriber = None
    google_subscriber = None
    regular_user = None
    google_user = None

    # Determine the subscriber (the user who is subscribing)
    if subscriber_type == 'google':
        try:
            # Find the Google user who is subscribing
            google_subscriber = GoogleUser.objects.get(id=subscriber_id)
        except GoogleUser.DoesNotExist:
            return Response({'message': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            # Find the regular user who is subscribing
            subscriber = User.objects.get(id=subscriber_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Determine the target user (the user being subscribed to)
    if user_type == 'google':
        try:
            # Find the Google user being subscribed to
            google_user = GoogleUser.objects.get(id=user_id)
        except GoogleUser.DoesNotExist:
            return Response({'message': 'Google user not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            # Find the regular user being subscribed to
            regular_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the subscription already exists
    subscription_exists = Subscription.objects.filter(
        user=subscriber if subscriber_type == 'regular' else None,
        google_user=google_subscriber if subscriber_type == 'google' else None,
        subscribed_to_user=regular_user if user_type == 'regular' else None,
        subscribed_to_google_user=google_user if user_type == 'google' else None
    ).exists()

    if subscription_exists:
        
        # Unsubscribe the user
        Subscription.objects.filter(
            user=subscriber if subscriber_type == 'regular' else None,
            google_user=google_subscriber if subscriber_type == 'google' else None,
            subscribed_to_user=regular_user if user_type == 'regular' else None,
            subscribed_to_google_user=google_user if user_type == 'google' else None
        ).delete()
        
            # Count the total number of subscriptions the user (or Google user) has
        if user_type == 'regular':
            subscription_count = Subscription.objects.filter(subscribed_to_user=regular_user).count()
        else:
            subscription_count = Subscription.objects.filter(subscribed_to_google_user=google_user).count()
            
        return Response({'message': 'unsubscribed', 
                             'subscription_count': subscription_count
                             },status=status.HTTP_200_OK)
    else:
        # Subscribe the user
        Subscription.objects.create(
            user=subscriber if subscriber_type == 'regular' else None,
            google_user=google_subscriber if subscriber_type == 'google' else None,
            subscribed_to_user=regular_user if user_type == 'regular' else None,
            subscribed_to_google_user=google_user if user_type == 'google' else None,
            user_type=subscriber_type  # Save the type of subscribing user (regular or Google)
        )

 # Count the total number of subscriptions the user (or Google user) has
    if user_type == 'regular':
        subscription_count = Subscription.objects.filter(subscribed_to_user=regular_user).count()
    else:
        subscription_count = Subscription.objects.filter(subscribed_to_google_user=google_user).count()

    return Response({
        'message': 'subscribed',
        'subscription_count': subscription_count  # Return the total number of subscriptions
    }, status=status.HTTP_201_CREATED)
    




class PropertyLikeCountView(APIView):
    def get(self, request, *args, **kwargs):
        # Count likes for regular properties
        regular_property_likes = (
            Like.objects
            .filter(property__isnull=False)  # Only regular properties
            .values('property')
            .annotate(like_count=Count('id'))
            .order_by('-like_count')
        )

        # Count likes for google properties
        google_property_likes = (
            Like.objects
            .filter(google_property__isnull=False)  # Only Google properties
            .values('google_property')
            .annotate(like_count=Count('id'))
            .order_by('-like_count')
        )

        # Combine the results into a single response
        combined_likes = {
            "regular_properties": list(regular_property_likes),
            "google_properties": list(google_property_likes),
        }

        return Response(combined_likes)





class SubscriptionCountView(APIView):
    def get(self, request, *args, **kwargs):
        # Count subscriptions for regular users
        regular_user_subscriptions = (
            Subscription.objects
            .filter(subscribed_to_user__isnull=False)  # Only regular users
            .values('subscribed_to_user')
            .annotate(subscription_count=Count('id'))
            .order_by('-subscription_count')
        )

        # Count subscriptions for Google users
        google_user_subscriptions = (
            Subscription.objects
            .filter(subscribed_to_google_user__isnull=False)  # Only Google users
            .values('subscribed_to_google_user')
            .annotate(subscription_count=Count('id'))
            .order_by('-subscription_count')
        )

        # Combine the results into a single response
        combined_subscriptions = {
            "regular_user_subscriptions": list(regular_user_subscriptions),
            "google_user_subscriptions": list(google_user_subscriptions),
        }

        return Response(combined_subscriptions)



