import random
import string
from .models import *

# Generating a random phone number with the format XXX-XXX-XXXX
def generate_random_phone_number():
    return f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

# Generating a random name using common first and last names
def generate_random_name():
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Olivia", "James", "Sophia", "William", "Ava"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Martinez"]
    return f"{random.choice(first_names)}_{random.choice(last_names)}"

# Generating a random email based on the provided name
def generate_random_email(name):
    name = name.replace("_", "").lower()
    domain = random.choice(["example.com", "gmail.com", "yahoo.com", "hotmail.com"])
    return f"{name}@{domain}"

# Generating a list of random contact details
def generate_random_information():
    lis = []
    for _ in range(10):
        phone_number = generate_random_phone_number()
        name = generate_random_name()
        email = generate_random_email(name)
        lis.append({'name': name, 'phone_number': phone_number, 'email': email})
    return lis

# Save a new user and their random contact information into the global database
def save_newuser_and_random_information(username, phone_number, email, flag):
    """
    Method to add information into the global database (ContactInformation model).
    This code can be replaced by the code for importing contacts from a user's device.
    """
    print(username, phone_number, email)
    try:
        if flag:
            contactinformation = ContactInformation(name=username, phone_number=phone_number, email=email, is_registered=True)
            contactinformation.save()
        contacts = generate_random_information()
        for contact in contacts:
            contactinformation = ContactInformation(name=contact['name'], phone_number=contact['phone_number'], email=contact['email'])
            contactinformation.save()

            # Maintain phonebook
            user = User.objects.get(username=username)            
            phonebook = Phonebook(user=user, name=contact['name'], phone_number=contact['phone_number'])
            phonebook.save()

    except Exception as e:
        print("Error while saving new user info and their contact list into the global database", e)

# Increment the search count for a given contact
def increase_search_count(contact):
    contact.search_counts += 1
    contact.save()
