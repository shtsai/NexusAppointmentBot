import requests
import logging
from datetime import datetime
from dataclasses import dataclass
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Testing id
LOCATION_IDS = {
    5020: "Blaine", 
    5161: "Niagara", 
    5223: "Testing"
}

URL_FORMAT = 'https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=10&locationId={0}&minimum=1'

@dataclass
class Slot:
    location_name: str
    time: str

def is_preferred_time(time):
    date_object = datetime.strptime(time, "%Y-%m-%dT%H:%M")
    day_of_week = date_object.weekday()

    # Friday, Saturday, Sunday
    if day_of_week in [4,5,6]:
        return True

    return False


def parse_slots(data, location_name):
    slots = []
    for row in data:
        start_time = row['startTimestamp']
        if is_preferred_time(start_time):
            slots.append(Slot(location_name=location_name,time=start_time))
    return slots

def fetch_available_slots():
    try:
        slots = []
        for location_id, location_name in LOCATION_IDS.items():
            data = requests.get(URL_FORMAT.format(location_id)).json()
            slots.extend(parse_slots(data, location_name))
        
        
        for slot in slots:
            print(slot)

    except Exception:
        logging.critical("Error when calling cbp API")

def send_email():
    message = Mail(
        # TODO: input email addresses
        from_email='EMAIL',
        to_emails='EMAIL',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        # TODO: input SendGrid API KEY
        sg = SendGridAPIClient('API_KEY')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def main():
    # fetch_available_slots()
    send_email()


if __name__ == '__main__':
    main()