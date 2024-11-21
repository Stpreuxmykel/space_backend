from django.urls import path
from .views import UserPropertyViewSet

urlpatterns = [
    path('create_property_user/', UserPropertyViewSet.as_view({'post': 'create'}), name='create_property_user'),
    path('update_property_user/<int:pk>/', UserPropertyViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='update_property_user'),
    path('delete_property_user/<int:pk>/', UserPropertyViewSet.as_view({'delete': 'destroy'}), name='delete_property_user'),
    path('retrieve_property_user/<int:pk>/', UserPropertyViewSet.as_view({'get': 'retrieve'}), name='retrieve_property_user'),
    path('list_property_user/', UserPropertyViewSet.as_view({'get': 'list'}), name='list_property_user'),
]
