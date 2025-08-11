# calendar_helper.py
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def create_calendar_event(name, phone, date_str, time_range, artist, services, calendar_id='spa.turquesa.manizales@gmail.com'):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=credentials)

    start_hour = int(time_range.split(':')[0])
    end_hour = int(time_range.split('-')[1].split(':')[0])
    duration = end_hour - start_hour

    start = datetime.strptime(f"{date_str} {start_hour:02d}:00", "%Y-%m-%d %H:%M")
    end = start + timedelta(hours=duration)

    timezone = pytz.timezone("America/Bogota")
    start = timezone.localize(start)
    end = timezone.localize(end)

    event = {
        'summary': f"Cita con {name} ({artist.capitalize()})\nTelefono: {phone}\nServicios: {services}",
        # 'description': f"Tel: {phone}\nServicios:\n{services}",
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'America/Bogota',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'America/Bogota',
        },
    }

    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event
