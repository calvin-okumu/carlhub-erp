from rest_framework import serializers
from .models import UserProfile, EmployeeDocument, CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'
        read_only_fields = ['user', 'uploaded_at', 'file_size', 'file_type']

# Update existing User serializer to include profile
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active',
                 'date_joined', 'profile']