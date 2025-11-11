from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Invoice, Session, PageEvent

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'client_name', 'amount', 'date', 'expiration_date', 'expiration_status_colored', 'status', 'toggle_done', 'created_by')
    list_filter = ('status', 'date', 'is_done', 'created_by')
    search_fields = ('invoice_no', 'client_name')
    date_hierarchy = 'date'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:invoice_id>/toggle-done/',
                self.admin_site.admin_view(self.toggle_done_view),
                name='invoices_invoice_toggle_done',
            ),
        ]
        return custom_urls + urls
    
    def toggle_done_view(self, request, invoice_id):
        """View to toggle the is_done status"""
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        invoice.is_done = not invoice.is_done
        invoice.save()
        
        status = 'marked as done' if invoice.is_done else 'marked as not done'
        messages.success(request, f'Invoice {invoice.invoice_no} has been {status}.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/invoices/invoice/'))
    
    def expiration_date(self, obj):
        """Display the expiration date"""
        return obj.get_expiration_date()
    expiration_date.short_description = 'Expiration Date'
    expiration_date.admin_order_field = 'date'
    
    def expiration_status_colored(self, obj):
        """Display expiration status with color coding"""
        color = obj.get_expiration_color()
        status = obj.get_expiration_status()
        
        color_map = {
            'green': '#28a745',  # Bootstrap green
            'orange': '#ffc107',  # Bootstrap orange/warning
            'red': '#dc3545'      # Bootstrap red/danger
        }
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color_map.get(color, '#000'),
            status
        )
    expiration_status_colored.short_description = 'Expiration Status'
    
    def toggle_done(self, obj):
        """Display a button to toggle done status"""
        if obj.is_done:
            button_text = 'Done'
            button_color = '#28a745'
        else:
            button_text = 'Not Done'
            button_color = '#dc3545'
        
        url = f'/admin/invoices/invoice/{obj.id}/toggle-done/'
        return format_html(
            '<a class="button" href="{}" style="background-color: {}; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 3px; font-weight: bold; display: inline-block;">{}</a>',
            url,
            button_color,
            button_text
        )
    toggle_done.short_description = 'Done Status'


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'start_time', 'end_time', 'duration', 'is_active')
    list_filter = ('start_time', 'end_time', 'user')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'start_time', 'end_time', 'duration')
    date_hierarchy = 'start_time'
    
    def is_active(self, obj):
        """Check if session is currently active"""
        return obj.end_time is None
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(PageEvent)
class PageEventAdmin(admin.ModelAdmin):
    list_display = ('page', 'user', 'session', 'start_time', 'end_time', 'duration', 'is_complete')
    list_filter = ('page', 'start_time', 'user')
    search_fields = ('page', 'user__username', 'session__session_id')
    readonly_fields = ('session', 'user', 'page', 'start_time', 'end_time', 'duration')
    date_hierarchy = 'start_time'
    
    def is_complete(self, obj):
        """Check if page event is complete (has end_time)"""
        return obj.end_time is not None
    is_complete.boolean = True
    is_complete.short_description = 'Complete'
