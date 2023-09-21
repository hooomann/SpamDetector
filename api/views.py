from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.helper import increase_search_count, save_newuser_and_random_information
from .models import ContactInformation, User, Phonebook
from .serializers import *
from rest_framework import generics
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.db.models import Q, F

class UserRegister(generics.CreateAPIView):
    """
    API endpoint for user registration.

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        # Extract username, phone_number, and email from request data
        username = self.request.data.get('username')
        phone_number = self.request.data.get('phone_number')
        email = self.request.data.get('email')
        flag = True

        # Check if the phone number exists in Contact Information table
        try:
            contact = ContactInformation.objects.get(phone_number=phone_number)
            contact.is_registered = True
            contact.name = username
            contact.email = email 
            contact.save()
            flag = False #if user information is already in the database we will not add it in the global database
        except ContactInformation.DoesNotExist:
            pass

        # Proceed with user registration
        serializer.save()

        # Call the method to save the new user and their phonebook information
        save_newuser_and_random_information(username, phone_number, email, flag)

#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################

class UserLogin(generics.CreateAPIView):
    """
    API endpoint for user login.

    Provides token if login successful
    """

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Extract username and password from request data
            username = request.data.get('username')
            password = request.data.get('password')
        
            # Authenticate user
            user = User.objects.get(username=username)
        
            # Check if authentication is successful
            if user and password == user.password:
                # Login the user
                login(request, user)

                # Generate or retrieve user's token
                token, created = Token.objects.get_or_create(user=user)

                # Return token in response
                return Response({'token': token.key})
            else:
                # Invalid credentials
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            # Handle the case when the user does not exist
            return Response({'error': 'User Not Found'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            # Handle any unexpected errors
            return Response({'error': 'An error occurred while logging in'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################


class UserLogout(generics.GenericAPIView):
    """
    API endpoint for user logout.

    Deletes token if logout successful
    """
    def post(self, request, *args, **kwargs):
        try:
            # Get the user's token from the request headers
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                token_scheme, token_key = auth_header.split(' ')
                if token_scheme == 'Bearer':
                    # Retrieve token based on the provided key
                    token = Token.objects.get(key=token_key)
                    user = token.user

                    # Delete the token
                    token.delete()

                    # Successful logout
                    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
            
            # Invalid or missing token
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Token.DoesNotExist:
            # Token not found
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({'error': 'An error occurred while logging out'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################


class MarkSpamAPI(APIView):
    """
    API endpoint for marking a phone number as spam.

    User has to be logged in to mark another number as spam
    """
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve token from the request headers
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                token_scheme, token_key = auth_header.split(' ')
                if token_scheme == 'Bearer':
                    # Retrieve user based on the provided token key
                    token = Token.objects.get(key=token_key)
                    user = token.user
                    
                    # Extract phone number from request data
                    serializer = MarkSpamSerializer(data=request.data)
                    if serializer.is_valid():
                        phone_number = serializer.validated_data['phone_number']
                        
                        # Mark the phone number as spam
                        contact = ContactInformation.objects.get(phone_number=phone_number)
                        contact.spam_reports = F('spam_reports') + 1
                        contact.save()
                        
                        return Response({'message': 'Phone number marked as spam'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            # Invalid or missing token
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Token.DoesNotExist:
            # Token not found
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except ContactInformation.DoesNotExist:
            # Contact not found
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################


class SearchContactAPI(APIView):
    """
    API endpoint for searching contacts based on a query.

    Name is checked for beginning and containing
    """
    def get(self, request, *args, **kwargs):
        contacts = []
        try:
            # Retrieve token from the request headers
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                token_scheme, token_key = auth_header.split(' ')
                if token_scheme == 'Bearer':
                    # Retrieve user based on the provided token key
                    token = Token.objects.get(key=token_key)
                    user = token.user
                    
                    # Extract search query from request parameters
                    search_query = request.query_params.get('q')
                    if search_query:
                        if not search_query.isdigit():
                            # Search for contact information based on the name
                            contacts_starting_with_query = ContactInformation.objects.filter(
                                Q(name__istartswith=search_query)
                            ).annotate(spam_likelihood=F('spam_reports') / F('search_counts'))
                            
                            contacts_containing_query = ContactInformation.objects.filter(
                                ~Q(name__istartswith=search_query),
                                Q(name__icontains=search_query)
                            ).annotate(spam_likelihood=F('spam_reports') / F('search_counts'))

                            contacts = contacts_starting_with_query.union(contacts_containing_query)
                        else:
                            # Search by phone number
                            registered_user = User.objects.filter(phone_number=search_query).first()
                            if registered_user:
                                # Return the result for a registered user with that phone number
                                contact = ContactInformation.objects.filter(phone_number=search_query, is_registered=True).first()
                                contacts.append(contact)
                                # Increment search_count for contact of the search result
                                increase_search_count(contact)
                            else:
                                # No registered user found, searching by phone number across all contacts
                                contacts = ContactInformation.objects.filter(phone_number=search_query)

                        
                        
                        serializer = SearchContactSerializer(contacts, many=True)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Search query parameter "q" is missing'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Invalid or missing token
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Token.DoesNotExist:
            # Token not found
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################
#####################################################################################################################################################################################


class ContactDetailAPI(APIView):
    """
    API endpoint for retrieving contact details.

    If the user is in the person's contact list and the person is a registered user with us.
    """
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve token from the request headers
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                token_scheme, token_key = auth_header.split(' ')
                if token_scheme == 'Bearer':
                    # Retrieve user based on the provided token key
                    token = Token.objects.get(key=token_key)
                    user = token.user
                    contacts = []
                    # Extract search query from request parameters
                    phone_number = request.query_params.get('q')
                    if phone_number:
                        person = User.objects.filter(phone_number=phone_number).first()
                        if person:
                            in_phonebook = Phonebook.objects.filter(user_id=person.id, phone_number=user.phone_number)
                            if in_phonebook:
                                contact = ContactInformation.objects.filter(phone_number=phone_number, is_registered=True).first()
                                serializer = ContactDetailSerializer(contact)
                            else:
                                contact = ContactInformation.objects.filter(phone_number=phone_number).first()
                                serializer = SearchContactSerializer(contact)
                        else:
                            contact = ContactInformation.objects.filter(phone_number=phone_number).first()
                            serializer = SearchContactSerializer(contact)
                        # Increment search_count for contact of the search result
                        increase_search_count(contact)   
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Search query parameter "q" is missing'}, status=status.HTTP_400_BAD_REQUEST)
                       
            # Invalid or missing token
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Token.DoesNotExist:
            # Token not found
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except ContactInformation.DoesNotExist:
            # Contact not found
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
