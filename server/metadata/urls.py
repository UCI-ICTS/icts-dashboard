# metadata/urls.py

from django.urls import path
from metadata.apis import GetMetadataAPI, SubmitParticipantAPI

urlpatterns = [
    path('get_metadata/', GetMetadataAPI.as_view()),
    path('submit_participant/', SubmitParticipantAPI.as_view())
]