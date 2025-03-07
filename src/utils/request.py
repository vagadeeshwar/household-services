from datetime import datetime, timedelta

from sqlalchemy import func

from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
)
from src.models import ProfessionalProfile, Service, ServiceRequest
from src.utils.cache import cache


def _get_cache_key_availability(professional_id: int, date: datetime.date) -> str:
    """Generate cache key for professional availability"""
    return f"availability:{professional_id}:{date.isoformat()}"


def _get_cache_key_schedule(
    professional_id: int, start_date: datetime.date, end_date: datetime.date
) -> str:
    """Generate cache key for professional schedule"""
    return f"schedule:{professional_id}:{start_date.isoformat()}:{end_date.isoformat()}"


def check_booking_availability(
    professional_id: int, preferred_time: datetime, service_duration: int
) -> tuple[bool, str | None]:
    """
    Check if a professional is available for a booking time slot.
    Args:
        professional_id: ID of the professional
        preferred_time: Requested start time
        service_duration: Service duration in minutes (must be an integer)

    Returns:
        Tuple of (is_available, error_message)
    """
    # Generate cache key for the day
    cache_key = _get_cache_key_availability(professional_id, preferred_time.date())

    # Try to get cached availability data
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        # Use cached data to check availability
        return _check_availability_from_cached_data(
            cached_data, preferred_time, service_duration
        )

    try:
        # Ensure service_duration is an integer
        duration_minutes = int(service_duration)
    except (TypeError, ValueError):
        return False, "Invalid service duration"

    # Calculate the end time of the requested booking
    booking_end_time = preferred_time + timedelta(minutes=duration_minutes)

    # Get all assigned requests for the professional
    assigned_requests = (
        ServiceRequest.query.join(Service)
        .filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
            # Get requests on the same day
            func.date(ServiceRequest.preferred_time) == preferred_time.date(),
        )
        .all()
    )

    # Prepare availability data for caching
    availability_data = []
    for request in assigned_requests:
        start = request.preferred_time
        end = start + timedelta(minutes=int(request.service.estimated_time))
        availability_data.append(
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "request_id": request.id,
            }
        )

    # Cache the availability data for 15 minutes
    cache.set(cache_key, availability_data, timeout=900)

    # Check for overlaps
    for existing_request in assigned_requests:
        existing_start = existing_request.preferred_time
        existing_end = existing_start + timedelta(
            minutes=int(existing_request.service.estimated_time)
        )

        # Check for any overlap
        if (
            (
                existing_start <= preferred_time < existing_end
            )  # New booking starts during existing
            or (
                existing_start < booking_end_time <= existing_end
            )  # New booking ends during existing
            or (
                preferred_time <= existing_start and booking_end_time >= existing_end
            )  # New booking encompasses existing
        ):
            return (
                False,
                "Professional has an overlapping booking during this time slot",
            )

    # Check if service extends beyond business hours (6 PM)
    end_time_limit = datetime.combine(
        preferred_time.date(), datetime.strptime("18:00", "%H:%M").time()
    )
    if booking_end_time > end_time_limit:
        return False, "Service cannot extend beyond 6 PM"

    return True, None


def _check_availability_from_cached_data(
    cached_data: list[dict], preferred_time: datetime, service_duration: int
) -> tuple[bool, str | None]:
    """Check availability using cached data"""
    booking_end_time = preferred_time + timedelta(minutes=service_duration)

    # Check business hours first
    end_time_limit = datetime.combine(
        preferred_time.date(), datetime.strptime("18:00", "%H:%M").time()
    )
    if booking_end_time > end_time_limit:
        return False, "Service cannot extend beyond 6 PM"

    # Check overlaps with cached bookings
    for booking in cached_data:
        existing_start = datetime.fromisoformat(booking["start"])
        existing_end = datetime.fromisoformat(booking["end"])

        if (
            (existing_start <= preferred_time < existing_end)
            or (existing_start < booking_end_time <= existing_end)
            or (preferred_time <= existing_start and booking_end_time >= existing_end)
        ):
            return (
                False,
                "Professional has an overlapping booking during this time slot",
            )

    return True, None


def generate_available_slots(
    start_date: datetime.date, end_date: datetime.date, slot_duration: int = 60
) -> list:
    """Generate available time slots for given date range"""
    slots = []
    current_date = start_date

    while current_date <= end_date:
        # Generate slots for business hours (9 AM to 6 PM)
        current_time = datetime.combine(
            current_date, datetime.min.time().replace(hour=9)
        )
        end_time = datetime.combine(current_date, datetime.min.time().replace(hour=18))

        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=slot_duration)
            if slot_end <= end_time:
                slots.append(
                    {
                        "start_time": current_time,
                        "end_time": slot_end,
                        "status": "available",
                        "service_request": None,
                    }
                )
            current_time = slot_end

        current_date += timedelta(days=1)

    return slots


def get_professional_schedule(
    professional_id: int,
    start_date: datetime.date,
    end_date: datetime.date,
    service_id: int | None = None,
) -> dict:
    """Get professional's schedule including booked and available slots"""

    # Try to get cached schedule
    cache_key = _get_cache_key_schedule(professional_id, start_date, end_date)
    cached_schedule = cache.get(cache_key)

    if cached_schedule is not None:
        return cached_schedule

    # Get professional's service duration
    professional = ProfessionalProfile.query.get_or_404(professional_id)
    if service_id:
        service = Service.query.get_or_404(service_id)
        slot_duration = service.estimated_time
    else:
        slot_duration = professional.service_type.estimated_time

    # Generate all possible time slots
    all_slots = generate_available_slots(start_date, end_date, slot_duration)

    # Get professional's bookings
    bookings = (
        ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status.in_(
                [
                    REQUEST_STATUS_ASSIGNED,
                    REQUEST_STATUS_COMPLETED,
                ]
            ),
            ServiceRequest.preferred_time
            >= datetime.combine(start_date, datetime.min.time()),
            ServiceRequest.preferred_time
            <= datetime.combine(end_date, datetime.max.time()),
        )
        .order_by(ServiceRequest.preferred_time)
        .all()
    )

    # Organize slots by date
    schedule = {}
    for slot in all_slots:
        date = slot["start_time"].date()
        if date not in schedule:
            schedule[date] = {
                "date": date,
                "time_slots": [],
                "total_slots": 0,
                "available_slots": 0,
                "booked_slots": 0,
            }
        schedule[date]["time_slots"].append(slot)
        schedule[date]["total_slots"] += 1
        schedule[date]["available_slots"] += 1

    # Mark booked slots
    for booking in bookings:
        booking_end = booking.preferred_time + timedelta(
            minutes=booking.service.estimated_time
        )
        booking_date = booking.preferred_time.date()

        if booking_date in schedule:
            for slot in schedule[booking_date]["time_slots"]:
                # Check if slot overlaps with booking
                if (
                    slot["start_time"] <= booking.preferred_time < slot["end_time"]
                    or slot["start_time"] < booking_end <= slot["end_time"]
                ):
                    slot["status"] = (
                        "booked"
                        if booking.status != REQUEST_STATUS_COMPLETED
                        else "completed"
                    )
                    slot["service_request"] = booking
                    schedule[booking_date]["available_slots"] -= 1
                    schedule[booking_date]["booked_slots"] += 1

    # Prepare response
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "days": list(schedule.values()),
        "total_bookings": len(bookings),
        "available_days": sum(
            1 for day in schedule.values() if day["available_slots"] > 0
        ),
    }

    # Cache the schedule for 5 minutes
    cache.set(cache_key, response, timeout=300)

    return response
