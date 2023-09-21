from rest_framework import serializers
from .models import *

#Serializer to register and login users
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}


#Serializer to take input to mark a Person's contact number as spam
class MarkSpamSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

#Serializer for showing search results
class SearchContactSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.SerializerMethodField()

    class Meta:
        model = ContactInformation
        fields = ('name', 'phone_number', 'spam_likelihood')

    def get_spam_likelihood(self, obj):
        if obj.search_counts > 0:
            return obj.spam_reports / obj.search_counts * 100
        return 0.0


# Serializer for showing contact details
class ContactDetailSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.SerializerMethodField()

    class Meta:
        model = ContactInformation
        fields = ('name', 'phone_number', 'spam_likelihood', 'email')

    def get_spam_likelihood(self, obj):
        if obj.search_counts > 0:
            return obj.spam_reports / obj.search_counts * 100
        return 0.0