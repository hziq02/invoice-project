from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, session_start, event_start, event_end, session_end

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    # Tracking endpoints
    path('track/session/start', session_start, name='session_start'),
    path('track/session/end', session_end, name='session_end'),
    path('track/event/start', event_start, name='event_start'),
    path('track/event/end', event_end, name='event_end'),
] + router.urls