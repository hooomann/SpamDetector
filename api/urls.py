from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegister.as_view(), name='user-register'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', UserLogout.as_view(), name='user-logout'),
    path('markspam/', MarkSpamAPI.as_view(), name='markspam'),
    path('search/', SearchContactAPI.as_view(), name='search-contact'),
    path('contactdetail/', ContactDetailAPI.as_view(), name='contact-detail'),
 
]
