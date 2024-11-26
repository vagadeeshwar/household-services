from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import or_, and_

from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_IN_PROGRESS,
    REQUEST_STATUS_COMPLETED,
)

from src.models import ServiceRequest, ProfessionalProfile, Service


def check_booking_availability(
    professional_id: int, preferred_time: datetime, duration_minutes: int
) -> Tuple[bool, Optional[str]]:
    """
    Check if a professional is available for a booking time slot.
    Returns: (is_available, error_message)
    """
    # Calculate the end time of the requested booking
    booking_end_time = preferred_time + timedelta(minutes=duration_minutes)

    # Find any overlapping bookings
    overlapping_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.status.in_(
            [REQUEST_STATUS_ASSIGNED, REQUEST_STATUS_IN_PROGRESS]
        ),
        or_(
            # Case 1: New booking starts during an existing booking
            and_(
                ServiceRequest.preferred_time <= preferred_time,
                ServiceRequest.preferred_time
                + timedelta(minutes=ServiceRequest.service.duration_minutes)
                > preferred_time,
            ),
            # Case 2: New booking ends during an existing booking
            and_(
                ServiceRequest.preferred_time < booking_end_time,
                ServiceRequest.preferred_time
                + timedelta(minutes=ServiceRequest.service.duration_minutes)
                >= booking_end_time,
            ),
            # Case 3: New booking completely encompasses an existing booking
            and_(
                ServiceRequest.preferred_time >= preferred_time,
                ServiceRequest.preferred_time
                + timedelta(minutes=ServiceRequest.service.duration_minutes)
                <= booking_end_time,
            ),
        ),
    ).first()

    if overlapping_requests:
        return False, "Professional has an overlapping booking during this time slot"

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
    service_id: Optional[int] = None,
) -> dict:
    """Get professional's schedule including booked and available slots"""

    # Get professional's service duration
    professional = ProfessionalProfile.query.get_or_404(professional_id)
    if service_id:
        service = Service.query.get_or_404(service_id)
        slot_duration = service.duration_minutes
    else:
        slot_duration = professional.service_type.duration_minutes

    # Generate all possible time slots
    all_slots = generate_available_slots(start_date, end_date, slot_duration)

    # Get professional's bookings
    bookings = (
        ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status.in_(
                [
                    REQUEST_STATUS_ASSIGNED,
                    REQUEST_STATUS_IN_PROGRESS,
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
            minutes=booking.service.duration_minutes
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

    return response
