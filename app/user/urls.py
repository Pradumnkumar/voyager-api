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
    path('create/',  views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('verify-otp/', views.VerifyOTPTokenView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('request-password-reset/',
         views.PasswordResetRequestView.as_view(),
         name='password_reset_request'
         ),
    path('reset-password/',
         views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'
         ),
]
