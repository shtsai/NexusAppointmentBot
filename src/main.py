import requests
import logging
from datetime import datetime
from dataclasses import dataclass


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

def main():
    fetch_available_slots()


if __name__ == '__main__':
    main()