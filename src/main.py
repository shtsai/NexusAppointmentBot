import requests
import time
from datetime import datetime
from dataclasses import dataclass
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
import random
from sendgrid.helpers.mail import Mail

# Testing id
LOCATION_IDS = {
    5020: "Blaine",
    5161: "Niagara",
    # 16656: "Detroit" # for testing
}

URL_FORMAT = "https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=150&locationId={0}&minimum=1"


@dataclass
class Slot:
    location_name: str
    time: str


def is_preferred_time(time):
    date_object = datetime.strptime(time, "%Y-%m-%dT%H:%M")
    day_of_week = date_object.weekday()

    # Friday, Saturday, Sunday
    if day_of_week in [4, 5, 6]:
        return True

    return False


def parse_slots(data, location_name):
    slots = []
    for row in data:
        start_time = row["startTimestamp"]
        if is_preferred_time(start_time):
            slots.append(Slot(location_name=location_name, time=start_time))
    return slots


def fetch_available_slots():
    try:
        slots = []
        for location_id, location_name in LOCATION_IDS.items():
            data = requests.get(URL_FORMAT.format(location_id)).json()
            slots.extend(parse_slots(data, location_name))

        return slots
    except Exception:
        print("Error when calling cbp API")


def send_email(api_key, from_email, to_emails, slots, human_readable_time):
    email_content = """
<p>I found the following appointment slots that matches your preference!</p>

<ul>
{}
</ul>

<p>Please go to https://ttp.cbp.dhs.gov/ to schedule your appointment.</p>
    """.format(
        "\n".join(
            ["<li>" + slot.location_name + " " + slot.time + "</li>" for slot in slots]
        )
    )
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject="Nexus Appointment Finder - " + human_readable_time,
        html_content=email_content,
    )
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print("successfully sent email, status code = " + str(response.status_code))
    except Exception as e:
        print("Error when sending email due to: " + e.message)


def main():
    api_key = "TODO"
    from_email = "TODO"
    to_emails = "TODO"
    interval_s = 5 * 60  # 5 mins

    while True:
        current_time = datetime.now()
        human_readable_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print("Current timestamp = " + human_readable_time)

        slots = fetch_available_slots()
        if len(slots) > 0:
            send_email(api_key, from_email, to_emails, slots, human_readable_time)
            print("- Found matching appointment slots! Email sent!")
        else:
            print("- Unable to find any slot that matches preference.")

        jitter_s = random.uniform(-10, 10)
        print(f"Retrying in {interval_s + jitter_s} seconds...")
        print()
        time.sleep(interval_s + jitter_s)


if __name__ == "__main__":
    main()
