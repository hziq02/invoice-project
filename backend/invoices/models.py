from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    invoice_no = models.CharField(max_length=20)
    client_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False, verbose_name='Done')

    def __str__(self):
        return self.invoice_no
    
    def get_expiration_date(self):
        """Returns the expiration date (5 days from invoice date)"""
        return self.date + timedelta(days=5)
    
    def get_days_until_expiration(self):
        """Returns the number of days until expiration (negative if expired)"""
        today = timezone.now().date()
        expiration_date = self.get_expiration_date()
        return (expiration_date - today).days
    
    def get_expiration_color(self):
        """
        Returns color based on days until expiration:
        - Green: 3 or more days remaining
        - Orange: 1-2 days remaining (days 4 and 5)
        - Red: Expired (past 5 days)
        """
        days_remaining = self.get_days_until_expiration()
        
        if days_remaining >= 3:
            return 'green'
        elif days_remaining >= 1:
            return 'orange'
        else:
            return 'red'
    
    def get_expiration_status(self):
        """Returns a human-readable expiration status"""
        days_remaining = self.get_days_until_expiration()
        
        if days_remaining >= 3:
            return f"{days_remaining} days remaining"
        elif days_remaining >= 1:
            return f"{days_remaining} day(s) remaining - Expiring soon"
        elif days_remaining == 0:
            return "Expires today"
        else:
            return f"Expired {abs(days_remaining)} day(s) ago"

class Session(models.Model):
    """
    Tracks user sessions - from when they open the app until they leave
    """
    session_id = models.CharField(max_length=100, unique=True)  # UUID from frontend
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Which user
    start_time = models.DateTimeField()  # When session started
    end_time = models.DateTimeField(null=True, blank=True)  # When session ended (null if still active)
    last_ping = models.DateTimeField(null=True, blank=True)  # Last heartbeat ping
    duration = models.IntegerField(null=True, blank=True)  # Total session duration in seconds
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user.username}"
    
    class Meta:
        ordering = ['-start_time']  # Newest sessions first


class PageEvent(models.Model):
    """
    Tracks individual page views - how long user stays on each page
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE)  # Which session this belongs to
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Which user
    page = models.CharField(max_length=200)  # Page path (e.g., "/dashboard", "/invoices/new")
    start_time = models.DateTimeField()  # When user entered the page
    end_time = models.DateTimeField(null=True, blank=True)  # When user left the page
    duration = models.IntegerField(null=True, blank=True)  # How long on page (in seconds)
    
    def __str__(self):
        return f"{self.user.username} - {self.page} ({self.duration}s)"
    
    class Meta:
        ordering = ['-start_time']  # Newest events first