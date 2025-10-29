import requests
import datetime
import time
import os

# === SETTINGS ===
STOP_ID = "00001"              # StopAreaCode for Station Sloterdijk
REFRESH_INTERVAL = 30          # seconds between updates

def get_schedule(stop_id):
    # Use the StopAreaCode endpoint
    url = f"http://v0.ovapi.nl/stopareacode/{stop_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def parse_buses(schedule):
    now = datetime.datetime.now(datetime.timezone.utc)
    departures = []

    for _, area_data in schedule.items():
        for _, stop_data in area_data.get("TimingPoints", {}).items():
            for _, vehicle in stop_data.get("Passes", {}).items():
                try:
                    line = vehicle.get("LinePublicNumber", "")
                    destination = vehicle.get("DestinationName50", "")
                    target_time = vehicle.get("TargetDepartureTime", "")
                    expected_time = vehicle.get("ExpectedDepartureTime", "")
                    transport_type = vehicle.get("TransportType", "BUS")

                    if not target_time or not line:
                        continue

                    target_dt = datetime.datetime.fromisoformat(target_time.replace("Z", "+00:00"))
                    expected_dt = (
                        datetime.datetime.fromisoformat(expected_time.replace("Z", "+00:00"))
                        if expected_time else target_dt
                    )

                    if expected_dt > now:
                        delay = int((expected_dt - target_dt).total_seconds() / 60)
                        minutes_left = int((expected_dt - now).total_seconds() / 60)
                        departures.append({
                            "line": line,
                            "dest": destination,
                            "type": transport_type,
                            "target": target_dt,
                            "expected": expected_dt,
                            "delay": delay,
                            "mins_left": minutes_left
                        })
                except Exception:
                    continue

    # sort by soonest expected departure
    departures.sort(key=lambda x: x["expected"])
    return departures[:10]  # show next 10 departures

def show_live_board():
    while True:
        os.system("clear")
        print("🚏  Live vertrektijden – Station Sloterdijk (StopArea 00001)")
        print("⏱  Laatste update:", datetime.datetime.now().strftime("%H:%M:%S"))
        print("-" * 90)

        try:
            schedule = get_schedule(STOP_ID)
            departures = parse_buses(schedule)

            if not departures:
                print("⚠️  Geen aankomende voertuigen gevonden.")
            else:
                for d in departures:
                    planned = d["target"].astimezone().strftime("%H:%M")
                    eta = d["expected"].astimezone().strftime("%H:%M")
                    delay = d["delay"]
                    mins = d["mins_left"]

                    if delay > 0:
                        delay_str = f"+{delay} min"
                    elif delay < 0:
                        delay_str = f"{abs(delay)} min te vroeg"
                    else:
                        delay_str = "op tijd"

                    print(f"{d['type']:<4} Lijn {d['line']:<3} → {d['dest']:<25} "
                          f"Gepland: {planned:<5} Verwacht: {eta:<5} "
                          f"({delay_str:>10})  → over {mins:>2} min")

        except Exception as e:
            print("❌  Fout bij ophalen data:", e)

        print("-" * 90)
        print(f"Volgende update over {REFRESH_INTERVAL} seconden…")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    show_live_board()
