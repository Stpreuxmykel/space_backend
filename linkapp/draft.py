
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

    # Check if the like already exists for this user and property
    like, created = Like.objects.get_or_create(
        user=regular_user,
        google_user=google_user,
        property=property_obj if property_type == 'regular' else None,
        google_property=property_obj if property_type == 'google' else None,
        user_type=user_type,
        property_type=property_type
    )

    if created:
        return Response({'message': 'Property liked successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'You already liked this property'}, status=status.HTTP_200_OK)

