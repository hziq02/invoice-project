from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Invoice, Session, PageEvent
from .serializers import InvoiceSerializer, SessionSerializer, PageEventSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Invoice.objects.all().select_related('created_by')
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ========== TRACKING VIEWS ==========

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def session_start(request):
    """POST /api/track/session/start - Create new session"""
    import logging
    logger = logging.getLogger(__name__)
    
    session_id = request.data.get('session_id')
    start_time = request.data.get('start_time')
    
    logger.info(f"Session start request - session_id: {session_id}, start_time: {start_time}, user: {request.user.id}")
    
    if not session_id or not start_time:
        logger.error("Missing required fields in session_start")
        return Response(
            {'error': 'Missing required fields: session_id and start_time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if session already exists
    existing_session = Session.objects.filter(session_id=session_id, user=request.user).first()
    if existing_session:
        # IMPORTANT: Check if session should be auto-ended FIRST
        # This handles case where user closed browser and reopened
        if existing_session.end_time is None and existing_session.last_ping:
            # Session is active, check if it should be ended (gap > 2 minutes)
            current_time = timezone.now()
            time_since_last_ping = current_time - existing_session.last_ping
            
            if time_since_last_ping > timedelta(minutes=2):
                # Session should be ended - auto-end it now
                logger.info(f"Auto-ending session in session_start - gap: {time_since_last_ping}")
                
                # End all active page events first
                active_page_events = PageEvent.objects.filter(
                    session=existing_session,
                    end_time__isnull=True
                )
                active_count = active_page_events.count()
                
                for page_event in active_page_events:
                    page_event.end_time = existing_session.last_ping
                    if page_event.start_time:
                        page_event.duration = int((page_event.end_time - page_event.start_time).total_seconds())
                    else:
                        page_event.duration = 0
                    page_event.save()
                    # Refresh to ensure it's saved
                    page_event.refresh_from_db()
                    logger.info(f"✅ Ended page event - id: {page_event.id}, page: {page_event.page}, end_time: {page_event.end_time}, duration: {page_event.duration}s")
                
                logger.info(f"Ended {active_count} active page event(s)")
                
                # End the session
                if existing_session.start_time:
                    existing_session.duration = int((existing_session.last_ping - existing_session.start_time).total_seconds())
                existing_session.end_time = existing_session.last_ping
                existing_session.save()
                logger.info(f"✅ Session auto-ended - end_time: {existing_session.end_time}, duration: {existing_session.duration}")
                
                # Refresh from database to get updated values
                existing_session.refresh_from_db()
        
        # Parse start_time string to datetime
        from django.utils.dateparse import parse_datetime
        start_time_dt = parse_datetime(start_time)
        
        if not start_time_dt:
            start_time_dt = timezone.now()
        elif timezone.is_naive(start_time_dt):
            start_time_dt = timezone.make_aware(start_time_dt)
        
        # Now check session status after potential auto-end
        if existing_session.end_time is not None:
            # Previous session was ended - user is starting a NEW session
            # Reset the ended session to start fresh
            existing_session.start_time = start_time_dt  # New start time (parsed datetime)
            existing_session.end_time = None  # Reset end_time
            existing_session.last_ping = start_time_dt
            existing_session.duration = None  # Reset duration
            existing_session.save()
            logger.info(f"✅ Session reset for new session - id: {existing_session.id}, start_time: {existing_session.start_time}, user: {existing_session.user.id}")
            serializer = SessionSerializer(existing_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Session still active - just update last_ping, keep original start_time
            existing_session.last_ping = start_time_dt
            existing_session.save()
            serializer = SessionSerializer(existing_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Parse start_time string to datetime
    from django.utils.dateparse import parse_datetime
    start_time_dt = parse_datetime(start_time)
    
    if not start_time_dt:
        # If parse fails, use timezone.now()
        start_time_dt = timezone.now()
    elif timezone.is_naive(start_time_dt):
        start_time_dt = timezone.make_aware(start_time_dt)
    
    serializer = SessionSerializer(data={
        'session_id': session_id,
        'user': request.user.id,
        'start_time': start_time_dt,
        'last_ping': start_time_dt,
    })
    
    if serializer.is_valid():
        session = serializer.save(user=request.user)
        logger.info(f"✅ Session created - id: {session.id}, session_id: {session.session_id}, start_time: {session.start_time}, user: {session.user.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Log errors for debugging
    logger.error(f"Session start validation errors: {serializer.errors}")
    logger.error(f"Request data: {request.data}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def event_start(request):
    """POST /api/track/event/start - Create new page event"""
    session_id = request.data.get('session_id')
    page = request.data.get('page')
    start_time_str = request.data.get('start_time')
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Event start request - session_id: {session_id}, page: {page}, start_time: {start_time_str}")
    
    if not session_id or not page or not start_time_str:
        logger.error("Missing required fields in event_start")
        return Response(
            {'error': 'Missing required fields: session_id, page, start_time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Try to get existing session, if not found, create it
        session = Session.objects.filter(session_id=session_id, user=request.user).first()
        
        if not session:
            # Session doesn't exist yet - create it automatically
            logger.warn(f"Session not found for event_start, creating new session - session_id: {session_id}, user: {request.user.id}")
            
            # Parse start_time for session creation
            from django.utils.dateparse import parse_datetime
            session_start_time = parse_datetime(start_time_str)
            if not session_start_time:
                session_start_time = timezone.now()
            elif timezone.is_naive(session_start_time):
                session_start_time = timezone.make_aware(session_start_time)
            
            # Create new session
            session = Session.objects.create(
                session_id=session_id,
                user=request.user,
                start_time=session_start_time,
                last_ping=session_start_time
            )
            logger.info(f"✅ Auto-created session - id: {session.id}, session_id: {session.session_id}, start_time: {session.start_time}")
        
        # Parse start_time string to datetime
        from django.utils.dateparse import parse_datetime
        start_time = parse_datetime(start_time_str)
        
        if not start_time:
            # If parse fails, use timezone.now()
            start_time = timezone.now()
            logger.warn(f"Failed to parse start_time '{start_time_str}', using current time")
        elif timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        
        serializer = PageEventSerializer(data={
            'session': session.id,
            'user': request.user.id,
            'page': page,
            'start_time': start_time,
        })
        
        if serializer.is_valid():
            page_event = serializer.save(user=request.user, session=session)
            # Refresh to ensure data is saved
            page_event.refresh_from_db()
            logger.info(f"✅ Page event created - id: {page_event.id}, page: {page_event.page}, start_time: {page_event.start_time}, session_id: {session.session_id}, user: {request.user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Page event validation errors: {serializer.errors}")
        logger.error(f"Request data: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in event_start: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def event_end(request):
    """POST /api/track/event/end - Update page event with end time"""
    session_id = request.data.get('session_id')
    page = request.data.get('page')
    end_time_str = request.data.get('end_time')
    duration = request.data.get('duration')
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Event end request - session_id: {session_id}, page: {page}, end_time: {end_time_str}, duration: {duration}")
    
    if not session_id or not page or not end_time_str:
        logger.error("Missing required fields in event_end")
        return Response(
            {'error': 'Missing required fields: session_id, page, end_time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = Session.objects.get(session_id=session_id, user=request.user)
        
        # Parse end_time string to datetime
        from django.utils.dateparse import parse_datetime
        end_time = parse_datetime(end_time_str)
        
        if not end_time:
            # If parse fails, use timezone.now()
            end_time = timezone.now()
            logger.warn(f"Failed to parse end_time '{end_time_str}', using current time")
        elif timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time)
        
        # Find the most recent page event for this page that hasn't ended
        page_event = PageEvent.objects.filter(
            session=session,
            page=page,
            end_time__isnull=True
        ).order_by('-start_time').first()
        
        if not page_event:
            logger.warn(f"No active page event found for page: {page}, session: {session_id}")
            return Response({'error': 'Page event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        logger.info(f"Found page event - id: {page_event.id}, page: {page_event.page}, start_time: {page_event.start_time}")
        
        # Update page event
        page_event.end_time = end_time
        
        # Calculate duration if not provided or if provided duration seems wrong
        if duration is not None:
            page_event.duration = int(duration)
        elif page_event.start_time:
            # Calculate from start_time and end_time
            page_event.duration = int((page_event.end_time - page_event.start_time).total_seconds())
        else:
            page_event.duration = 0
        
        # Save to database
        page_event.save()
        # Refresh from database to ensure it's saved
        page_event.refresh_from_db()
        logger.info(f"✅ Page event ended - id: {page_event.id}, page: {page_event.page}, end_time: {page_event.end_time}, duration: {page_event.duration}s, session_id: {session.session_id}, user: {request.user.id}")
        
        serializer = PageEventSerializer(page_event)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        logger.error(f"Session not found - session_id: {session_id}, user: {request.user.id}")
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in event_end: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ping(request):
    """POST /api/track/ping - Update session heartbeat"""
    session_id = request.data.get('session_id')
    timestamp = request.data.get('timestamp')
    
    if not session_id or not timestamp:
        return Response(
            {'error': 'Missing required fields: session_id and timestamp'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = Session.objects.get(session_id=session_id, user=request.user)
        
        # Parse timestamp string to datetime (ensure timezone-aware)
        # Frontend sends ISO string in UTC (e.g., "2024-01-15T10:00:00.000Z")
        from django.utils.dateparse import parse_datetime
        
        ping_time = parse_datetime(timestamp)
        
        # Ensure ping_time is timezone-aware
        # parse_datetime handles ISO strings with 'Z' (UTC) and returns timezone-aware
        if not ping_time:
            # If parse_datetime fails, use timezone.now() as fallback
            # timezone.now() respects TIME_ZONE setting (Asia/Kuala_Lumpur)
            ping_time = timezone.now()
        elif timezone.is_naive(ping_time):
            # If it returns naive datetime (shouldn't happen with ISO strings), make it timezone-aware
            ping_time = timezone.make_aware(ping_time)
        
        # IMPORTANT: Store OLD last_ping BEFORE updating (to check time gap)
        old_last_ping = session.last_ping
        current_time = timezone.now()  # Already timezone-aware
        
        # Debug: Check what we have
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Ping received - session_id: {session_id}, old_last_ping: {old_last_ping}, session.end_time: {session.end_time}")
        
        # Check if session should be auto-ended BEFORE updating last_ping
        # This checks the gap between the OLD last_ping and NOW
        # Only check if: old_last_ping exists, session not already ended, and session has start_time
        if old_last_ping is not None and session.start_time and not session.end_time:
            # Calculate time difference
            # Both should be timezone-aware (Django stores timezone-aware by default)
            time_since_last_ping = current_time - old_last_ping
            
            # Debug logging (remove in production)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Ping check - old_last_ping: {old_last_ping}, current_time: {current_time}, gap: {time_since_last_ping}, threshold: {timedelta(minutes=2)}")
            
            if time_since_last_ping > timedelta(minutes=2):
                # Session inactive for too long - end it
                logger.info(f"Ending session - gap of {time_since_last_ping} exceeds {timedelta(minutes=2)}")
                
                # Calculate duration first
                duration_seconds = 0
                if session.start_time:
                    duration_seconds = int((old_last_ping - session.start_time).total_seconds())
                
                # IMPORTANT: End all active page events for this session
                # Get all page events that haven't ended yet
                active_page_events = PageEvent.objects.filter(
                    session=session,
                    end_time__isnull=True
                )
                
                # Count before processing
                active_count = active_page_events.count()
                
                # End all active page events with session end_time
                for page_event in active_page_events:
                    page_event.end_time = old_last_ping  # Use session end_time
                    if page_event.start_time:
                        page_event.duration = int((page_event.end_time - page_event.start_time).total_seconds())
                    else:
                        page_event.duration = 0
                    page_event.save()
                    # Refresh to ensure it's saved
                    page_event.refresh_from_db()
                    logger.info(f"✅ Ended page event - id: {page_event.id}, page: {page_event.page}, end_time: {page_event.end_time}, duration: {page_event.duration}s")
                
                logger.info(f"Ended {active_count} active page event(s)")
                
                # Use update() for atomic database operation to ensure end_time is saved
                Session.objects.filter(id=session.id).update(
                    end_time=old_last_ping,
                    duration=duration_seconds,
                    last_ping=ping_time  # Update last_ping at the same time
                )
                
                # Refresh session object from database to get updated values
                session.refresh_from_db()
                
                logger.info(f"✅ Session ended - end_time: {session.end_time}, duration: {session.duration}, last_ping: {session.last_ping}")
            else:
                logger.info(f"Session still active - gap of {time_since_last_ping} is less than {timedelta(minutes=2)}")
                # Update last_ping only (session not ended)
                session.last_ping = ping_time
                session.save()
        else:
            # Condition not met - just update last_ping
            logger.info(f"Auto-end check skipped - old_last_ping: {old_last_ping}, start_time: {session.start_time}, end_time: {session.end_time}")
            session.last_ping = ping_time
            session.save()
        
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)