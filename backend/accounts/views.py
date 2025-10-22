from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, EmployeeDocument
from .serializers import UserProfileSerializer, EmployeeDocumentSerializer

# Create your views here.

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class EmployeeDocumentListView(generics.ListCreateAPIView):
    """List and create employee documents"""
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.documents.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EmployeeDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete employee documents"""
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.documents.all()
