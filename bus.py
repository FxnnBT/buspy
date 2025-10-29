import requests
import datetime

# Halte-ID van Station Sloterdijk (Contactweg-zijde)
STOP_ID = "30002366"
LINE_NUMBER = "22"
DIRECTION = "Muiderpoortstation"

def get_schedule(stop_id):
    url = f"https://v0.ovapi.nl/tpc/{stop_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def find_next_bus(schedule, line, direction):
    now = datetime.datetime.now()
    next_times = []

    # OVAPI levert data genest onder stop_id
    for _, stop_data in schedule.items():
        for _, vehicle in stop_data.get("Passes", {}).items():
            data = vehicle.get("DestinationName", "")
            line_num = vehicle.get("LinePublicNumber", "")
            aimed_time = vehicle.get("TargetDepartureTime", "")
            if not aimed_time:
                continue
            if line_num == line and direction.lower() in data.lower():
                t = datetime.datetime.fromisoformat(aimed_time.replace("Z", "+00:00"))
                if t > now:
                    next_times.append(t)

    if next_times:
        return min(next_times)
    return None

def main():
    schedule = get_schedule(STOP_ID)
    next_bus = find_next_bus(schedule, LINE_NUMBER, DIRECTION)
    if next_bus:
        print(f"🚌 De eerstvolgende buslijn {LINE_NUMBER} naar {DIRECTION} vertrekt om {next_bus.strftime('%H:%M:%S')}")
    else:
        print(f"Geen aankomende rit gevonden voor lijn {LINE_NUMBER} naar {DIRECTION} bij halte {STOP_ID}.")

if __name__ == "__main__":
    main()
