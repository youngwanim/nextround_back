from django.urls import path
from rana.event import views_event

urlpatterns = [
    path('<event_id>', views_event.EventInfo.as_view(), name='event'),
    path('', views_event.EventList.as_view(), name='events'),
]
