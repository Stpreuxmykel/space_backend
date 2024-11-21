from rest_framework import serializers
from django.contrib.auth.models import User


from .models import *

class GoogleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleUser
        fields = ['id', 'name', 'email', 'token_id',  'created_at']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','email')






class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    

    class Meta:
        model = UserProfile
        fields = [
            'user', 'id', 'firstname', 'lastname', 'country','phone_number', 'city', 'state', 'address',
            'profile_picture', 'imageUrl', 'user', 'created_at'
        ]





class UserGoogleProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GoogleUserProfile
        fields = [
            'id', 'user',  'country', 'city', 'state', 'address',
            'profile_picture', 'imageUrl', 'phone_number',  'created_at'
        ]



class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['name', 'user_id']



class InterestGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestGoogle
        fields = ['user', 'name']



class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'imageUrl', 'uploaded_at']





class GooglePropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GooglePropertyImage
        fields = ['id', 'image', 'uploaded_at']


class GoogleUserPropertySerializer(serializers.ModelSerializer):
    phone_user = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    images = GooglePropertyImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False  # Make it optional to avoid errors if not provided
    )

    class Meta:
        model = GoogleUserProperty
        fields = ['user','id', 'property_id', 'author_image', 'author_name', 'new_phone_number', 'status', 'decision', 'phone_user', 'currency', 'city', 'state', 'title', 'address', 'description', 'price', 'type',
                  'images', 'uploaded_images', 'is_archived', 'status', 'country', 'category']
    
    def get_phone_user(self, obj):
        """
        Retrieve the phone number of the associated GoogleUserProfile.
        """
        # Assuming your Property model has a ForeignKey to GoogleUserProfile
        try:
            google_user_profile = GoogleUserProfile.objects.get(user=obj.user)  # Adjust if necessary
            return google_user_profile.phone_number if google_user_profile else None
        except GoogleUserProfile.DoesNotExist:
            return None
        

    def get_author_image(self, obj):
        try:
            google_owner_image = GoogleUserProfile.objects.get(user=obj.user)  # Adjust if necessary
            return google_owner_image.profile_picture.url if google_owner_image.profile_picture else None 
        except GoogleUserProfile.DoesNotExist:
            return None 
        


    def get_author_name(self, obj):
        try:
            google_owner_name = GoogleUser.objects.get(email=obj.user.email)
            return google_owner_name.name if google_owner_name else None 
        except GoogleUser.DoesNotExist:
            return None 


    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        user_property = GoogleUserProperty.objects.create(**validated_data)

        # Debug: Print uploaded_images to verify data
        print(f"Uploaded images: {uploaded_images}")

        # Save the uploaded images
        for image in uploaded_images:
            print(f"Saving image: {image}")  # Debugging line
            GooglePropertyImage.objects.create(property=user_property, image=image)

        return user_property

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])

        # Update the UserProperty fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new uploaded images
        for image in uploaded_images:
            print(f"Saving image: {image}")  # Debugging line
            GooglePropertyImage.objects.create(property=instance, image=image)

        return instance


class UserPropertySerializer(serializers.ModelSerializer):
    phone_user = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    images = PropertyImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False  # Make it optional to avoid errors if not provided
    )

    class Meta:
        model = UserProperty
        fields = ['user', 'id', 'currency', 'author_image', 'author_name', 'new_phone_number', 'status','decision','phone_user', 'city', 'state', 'address', 'property_id', 'title', 'description', 'price', 'type',
                  'images', 'uploaded_images', 'is_archived', 'status', 'country', 'category']
    def get_phone_user(self, obj):
        """
        Retrieve the phone number of the associated GoogleUserProfile.
        """
        # Assuming your Property model has a ForeignKey to GoogleUserProfile
        try:
           user_profile = UserProfile.objects.get(user=obj.user)  # Adjust if necessary
           return user_profile.phone_number if user_profile else None
        except UserProfile.DoesNotExist:
            return None
        
    def get_author_image(self, obj):
            """
            Retrieve the user_profile image of the associated UserProfile.
            """
            # Assuming your Property model has a ForeignKey to GoogleUserProfile
            try:
                user_profile = UserProfile.objects.get(user=obj.user)  # Adjust if necessary
                return user_profile.profile_picture.url if user_profile.profile_picture else None
            except UserProfile.DoesNotExist:
                return None
        
    def get_author_name(self, obj):
            """
            Retrieve the user_profile_nameof the associated UserProfile.
            """
            # Assuming your Property model has a ForeignKey to GoogleUserProfile
            try:
                user_profile_name = UserProfile.objects.get(user=obj.user)  # Adjust if necessary
                return user_profile_name.firstname + " " + user_profile_name.lastname if user_profile_name else None
            except UserProfile.DoesNotExist:
                return None


    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        user_property = UserProperty.objects.create(**validated_data)

        # Debug: Print uploaded_images to verify data
        print(f"Uploaded images: {uploaded_images}")

        # Save the uploaded images
        for image in uploaded_images:
            PropertyImage.objects.create(property=user_property, image=image)

        return user_property

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update the UserProperty fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new uploaded images
        for image in uploaded_images:
            PropertyImage.objects.create(property=instance, image=image)

        return instance


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = [
            "user", "google_user","user_type", "property",
              "google_property", "property_type", "liked_at"
        ]



class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'



  
    


