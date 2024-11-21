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
        return Response({'message': 'unsubscribed'}, status=status.HTTP_200_OK)
    else:
        # Subscribe the user
        Subscription.objects.create(
            user=subscriber if subscriber_type == 'regular' else None,
            google_user=google_subscriber if subscriber_type == 'google' else None,
            subscribed_to_user=regular_user if user_type == 'regular' else None,
            subscribed_to_google_user=google_user if user_type == 'google' else None,
            user_type=subscriber_type  # Save the type of subscribing user (regular or Google)
        )
        return Response({'message': 'subscribed'}, status=status.HTTP_201_CREATED)
