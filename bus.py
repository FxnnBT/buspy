import requests
import datetime
import time
import os

# === SETTINGS ===
STOP_ID = "30002366"           # Station Sloterdijk (Contactweg side)
LINE_NUMBER = "22"
DIRECTION = "Muiderpoortstation"
REFRESH_INTERVAL = 60          # seconds between updates

def get_schedule(stop_id):
    # Use HTTP (not HTTPS) to avoid SSL issues
    url = f"http://v0.ovapi.nl/tpc/{stop_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def find_next_bus(schedule, line, direction):
    now = datetime.datetime.now(datetime.timezone.utc)
    next_times = []

    for _, stop_data in schedule.items():
        for _, vehicle in stop_data.get("Passes", {}).items():
            destination = vehicle.get("DestinationName", "")
            line_num = vehicle.get("LinePublicNumber", "")
            aimed_time = vehicle.get("TargetDepartureTime", "")
            if not aimed_time:
                continue

            try:
                t = datetime.datetime.fromisoformat(
                    aimed_time.replace("Z", "+00:00")
                )
            except Exception:
                continue

            if line_num == line and direction.lower() in destination.lower() and t > now:
                next_times.append(t)

    return min(next_times) if next_times else None

def show_live_updates():
    while True:
        os.system("clear")
        print("🚏  Bus tracker – lijn", LINE_NUMBER, "naar", DIRECTION)
        print("📍  Halte-ID:", STOP_ID)
        print("⏱  Laatste update:", datetime.datetime.now().strftime("%H:%M:%S"))
        print("-" * 50)

        try:
            schedule = get_schedule(STOP_ID)
            next_bus = find_next_bus(schedule, LINE_NUMBER, DIRECTION)
            if next_bus:
                local_time = next_bus.astimezone().strftime("%H:%M:%S")
                mins_left = int((next_bus - datetime.datetime.now(datetime.timezone.utc)).total_seconds() / 60)
                print(f"🚌  Volgende bus vertrekt om {local_time}  ({mins_left} min)")
            else:
                print("⚠️  Geen aankomende bus gevonden.")
        except Exception as e:
            print("❌  Fout bij ophalen data:", e)

        print("-" * 50)
        print(f"Volgende update over {REFRESH_INTERVAL} s…")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    show_live_updates()
