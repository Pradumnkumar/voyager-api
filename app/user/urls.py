"""
URL mappings for the user API
"""

from django.urls import path

from user import views

# when this app_name is used for the reverse mapping that
# is defined when we do `revese('user:...')` when testing
app_name = 'user'

urlpatterns = [
    # Param1: Defines the url. So any request made to this url
    #         will be handled by Param2
    # Param2: As django expects a function call we add as_view()
    #         to get the function
    # Param3: name is used for the reverse lookup, so, reverse('user:create')
    #         will now point to this url
    path('create/',  views.CreateUserView.as_view(), name='create')
]
