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
        # Parse start_time string to datetime FIRST
        from django.utils.dateparse import parse_datetime
        start_time_dt = parse_datetime(start_time)
        
        if not start_time_dt:
            start_time_dt = timezone.now()
        elif timezone.is_naive(start_time_dt):
            start_time_dt = timezone.make_aware(start_time_dt)
        
        # Check session status
        existing_session.refresh_from_db()  # Refresh to get latest end_time
        
        if existing_session.end_time is not None:
            # Previous session was ended - user is starting a NEW session
            # Reset the ended session to start fresh
            logger.info(f"Resetting ended session for new session - id: {existing_session.id}")
            existing_session.start_time = start_time_dt  # New start time
            existing_session.end_time = None  # Reset end_time
            existing_session.duration = None  # Reset duration
            existing_session.save()
            logger.info(f"Session reset for new session - id: {existing_session.id}, start_time: {existing_session.start_time}, user: {existing_session.user.id}")
            serializer = SessionSerializer(existing_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Session still active - keep original start_time, just return existing session
            logger.info(f"Session still active - returning existing session - id: {existing_session.id}")
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
    })
    
    if serializer.is_valid():
        session = serializer.save(user=request.user)
        logger.info(f"Session created - id: {session.id}, session_id: {session.session_id}, start_time: {session.start_time}, user: {session.user.id}")
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
                start_time=session_start_time
            )
            logger.info(f"Auto-created session - id: {session.id}, session_id: {session.session_id}, start_time: {session.start_time}")
        
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
            logger.info(f"Page event created - id: {page_event.id}, page: {page_event.page}, start_time: {page_event.start_time}, session_id: {session.session_id}, user: {request.user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Page event validation errors: {serializer.errors}")
        logger.error(f"Request data: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in event_start: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def event_end(request):
    """POST /api/track/event/end - Update page event with end time
    
    Supports token in body (for sendBeacon) or Authorization header (for normal requests)
    Note: permission_classes removed to allow token in body authentication
    """
    # Handle token from body (for sendBeacon) or header (for normal requests)
    token_from_body = request.data.get('token')
    if token_from_body:
        # Token in body - authenticate manually
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            validated_token = UntypedToken(token_from_body)
            user_id = validated_token['user_id']
            user = User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Invalid token in body: {str(e)}")
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        # Use authenticated user from header (requires IsAuthenticated)
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
    
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
        session = Session.objects.get(session_id=session_id, user=user)
        
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
        logger.info(f"Page event ended - id: {page_event.id}, page: {page_event.page}, end_time: {page_event.end_time}, duration: {page_event.duration}s, session_id: {session.session_id}, user: {user.id}")
        
        serializer = PageEventSerializer(page_event)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        logger.error(f"Session not found - session_id: {session_id}, user: {user.id}")
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in event_end: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def session_end(request):
    """POST /api/track/session/end - Explicitly end session (hybrid approach)
    
    Supports token in body (for sendBeacon) or Authorization header (for normal requests)
    Note: permission_classes removed to allow token in body authentication
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Handle token from body (for sendBeacon) or header (for normal requests)
    token_from_body = request.data.get('token')
    if token_from_body:
        # Token in body - authenticate manually
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            validated_token = UntypedToken(token_from_body)
            user_id = validated_token['user_id']
            user = User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.error(f"Invalid token in body: {str(e)}")
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        # Use authenticated user from header (requires IsAuthenticated)
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
    
    session_id = request.data.get('session_id')
    end_time = request.data.get('end_time')
    
    if not session_id or not end_time:
        return Response(
            {'error': 'Missing required fields: session_id and end_time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = Session.objects.get(session_id=session_id, user=user)
        
        # If session already ended, just return success
        if session.end_time is not None:
            logger.info(f"Session already ended - session_id: {session_id}, user: {user.id}")
            serializer = SessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Parse end_time string to datetime
        from django.utils.dateparse import parse_datetime
        end_time_dt = parse_datetime(end_time)
        
        if not end_time_dt:
            end_time_dt = timezone.now()
        elif timezone.is_naive(end_time_dt):
            end_time_dt = timezone.make_aware(end_time_dt)
        
        logger.info(f"Ending session explicitly - session_id: {session_id}, end_time: {end_time_dt}, user: {user.id}")
        
        # Calculate duration
        duration_seconds = 0
        if session.start_time:
            duration_seconds = int((end_time_dt - session.start_time).total_seconds())
        
        # IMPORTANT: End all active page events for this session
        active_page_events = PageEvent.objects.filter(
            session=session,
            end_time__isnull=True
        )
        
        active_count = active_page_events.count()
        
        # End all active page events with session end_time
        for page_event in active_page_events:
            page_event.end_time = end_time_dt
            if page_event.start_time:
                page_event.duration = int((page_event.end_time - page_event.start_time).total_seconds())
            else:
                page_event.duration = 0
            page_event.save()
            page_event.refresh_from_db()
            logger.info(f"Ended page event - id: {page_event.id}, page: {page_event.page}, end_time: {page_event.end_time}, duration: {page_event.duration}s")
        
        logger.info(f"Ended {active_count} active page event(s)")
        
        # Update session with end_time and duration
        Session.objects.filter(id=session.id).update(
            end_time=end_time_dt,
            duration=duration_seconds
        )
        
        # Refresh session object from database
        session.refresh_from_db()
        
        logger.info(f"Session ended explicitly - end_time: {session.end_time}, duration: {session.duration}s")
        
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        logger.error(f"Session not found - session_id: {session_id}, user: {request.user.id}")
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in session_end: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)