from rest_framework import serializers
from .models import Invoice, Session, PageEvent

class InvoiceSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_no', 'client_name', 'amount', 'date', 'status', 
                  'description', 'is_done', 'created_by', 'created_by_username']
        
class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Session model
    Converts Session objects to/from JSON for API
    Note: last_ping is deprecated and not used (kept for backward compatibility)
    """
    class Meta:
        model = Session
        fields = ['id', 'session_id', 'user', 'start_time', 'end_time', 'last_ping', 'duration']
        read_only_fields = ['id']  # ID is auto-generated, can't be set manually


class PageEventSerializer(serializers.ModelSerializer):
    """
    Serializer for PageEvent model
    Converts PageEvent objects to/from JSON for API
    """
    class Meta:
        model = PageEvent
        fields = ['id', 'session', 'user', 'page', 'start_time', 'end_time', 'duration']
        read_only_fields = ['id']  # ID is auto-generated, can't be set manually
