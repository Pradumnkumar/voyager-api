"""
URL mappings for the user API
"""

from django.urls import path

from sector_assessment import views

# when this app_name is used for the reverse mapping that
# is defined when we do `revese('user:...')` when testing
app_name = 'sector_assessment'

urlpatterns = [
    # Param1: Defines the url. So any request made to this url
    #         will be handled by Param2
    # Param2: As django expects a function call we add as_view()
    #         to get the function
    # Param3: name is used for the reverse lookup, so, reverse('user:create')
    #         will now point to this url
    path('sectors/',  views.SectorListView.as_view(),
         name='sector-list'),

    path('skills/',  views.SkillListView.as_view(),
         name='skill-list'),

    path('question/<int:pk>',
         views.QuestionView.as_view({'get': 'retrieve'}),
         name='question'),

    path('assessment/',
         views.AssessmentView.as_view({'get': 'list'}),
         name='assessment'),

    path('assessment-run/',
         views.AssessmentRunView.as_view({'get': 'list'}),
         name='assessment-run'),

    path('assessment-run/post',
         views.AssessmentRunView.as_view({'post': 'create'}),
         name='assessment-run'),

    path('result/<int:pk>',
         views.ResultView.as_view({'get': 'retrieve'}),
         name='result'),
]
