from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
# from django.contrib.auth import views as auth_views
from .views import PasswordResetAPIView, PasswordResetConfirmAPIView

urlpatterns = [


    path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset_api'),
    path('password_reset_confirm/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm_api'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('google-signin/', GoogleSinUpView.as_view(), name='google-signin'),
    path('create_user_profile/', UserProfileListCreateView.as_view(), name='create_user_profile'),

    path('recommendations/<str:user_type>/<int:user_id>/', InterestAlgorithmRecommendationView.as_view(), name='interest-recommendations'),

    path('update_userprofile/<int:pk>/', UserUpdateProfileDetailView.as_view(), name='update_userprofile'),
    path('update_google_name/<int:pk>/', GoogleUserUpdateProfileDetailView.as_view(), name='update_google_name'),
    path('update_google/<int:pk>/', GoogleMoreUpdateProfileDetailView.as_view(), name='update_google_name'),


    path('get_property/<str:state>/', SpecificProperties.as_view(), name='get_property'),
    
    path('subscribed-properties/<str:subscriber_type>/<int:subscriber_id>/', SubscribedPropertiesView.as_view(), name='subscribed-properties'),

    path('property-search/', PropertySearchView.as_view(), name='property-search'),
    
    

    path('update_user_property_image/<int:pk>/', ImageUserPropertyUpdate.as_view(), name='update_user_property_image'),

    path('update_google_user_property_image/<int:pk>/', ImageGoolgeUserPropertyUpdate.as_view(), name='update_google_user_property_image'),


    path('country_city_region/', views.country_city_region_view, name='country_city_region'),


    path('create_user_google_profile/', UserGoogleProfileListCreateView.as_view(), name='create_user_google_profile'),
    
    path('create_user_interests/', UserInterestListCreateView.as_view(), name='create_user_interests'),
    path('create_user_google_interests/', InterestGoogleListCreateView.as_view(), name='create_user_google_interests'),
    path('google-user-token/<str:email>/', GoogleUserTokenView.as_view(), name='google-user-token'),

    path('specific_google_user/<int:id>/', SpecificGoogleUser.as_view(), name='specific_google_user'),

    

    path('get-google-user-profile/<str:email>/', GetGoogleUserProfile.as_view(), name='get-google-user-profile'),
    path('get_name/<str:email>/', GetNameGoogle.as_view(), name='get_name'),
    
    path('get-user-profile/', GetUserProfile.as_view(), name='get-user-profile'),

    path('get-user-google-interest/<str:email>/', GetGoogleUserInterest.as_view(), name='get-user-google-interest'),
    
    path('get-user-interest/', GetUserInterest.as_view(), name='get-user-interest'),

     path('get-property/<str:property_id>/', GetSpecificProperties.as_view(), name='get-property'),
     path('google_r/<int:user_id>/', GooglePropsRecommendations.as_view(), name='google_r'),
     path('regular_r/<int:user_id>/', RegularPropsRecommendations.as_view(), name='regular_r'),
     
     
    path('create_property_user/', UserPropertyViewSet.as_view({'post': 'create'}), name='create_property_user'),
    path('update_property_user/<int:pk>/', UserPropertyViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='update_property_user'),

    path('delete_property_user/<int:pk>/', UserPropertyViewSet.as_view({'delete': 'destroy'}), name='delete_property_user'),


    path('google_create_property_user/', GoogleUserPropertyViewSet.as_view({'post': 'create'}), name='google_create_property_user'),

    path('google_update_property_user/<int:pk>/', GoogleUserPropertyViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='google_update_property_user'),

     path('delete_property_google_user/<int:pk>/', GoogleUserPropertyViewSet.as_view({'delete': 'destroy'}), name='delete_property_google_user'),

    path('user_data/<int:id>/', GetUserInfo.as_view(), name='get-user_data'),

    path('google_user_data/<int:id>/', GetGoogleUserInfo.as_view(), name='google_user_data'),


    path('properties/', GoogleAllData.as_view(), name='properties'),
    path('actual_user_data/', MyUserProfileListCreateView.as_view(), name='actual_user_data'),


    path('actual_goolge_user_properties/<int:id>/', GetPropertiesGoogle.as_view(), name='actual_goolge_user_properties'),
    
    #   test delete
    path('actual_user_properties/<int:user>/', GetPropertiesUser.as_view(), name='actual_user_properties'),

    path('get_likes/<int:id>/<str:user_type>/', GetLikeGoogle.as_view(), name='get_likes'),

    path('get_subs/<int:id>/<str:user_type>/', GetSubscriptionsData.as_view(), name='get_subs'),

    

    path('like_property/<int:property_id>/<str:property_type>/<str:user_type>/', views.like_property, name='like_property'),
    path('subscribe/<int:user_id>/<str:user_type>/', views.subscribe_to_user, name='subscribe'),
    
    path('property_likes/', PropertyLikeCountView.as_view(), name='property_like_count'),
    path('get_subscriptions/', SubscriptionCountView.as_view(), name='get_subscriptions'),
     

    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


