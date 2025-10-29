import requests
import datetime
import time
import os

# === SETTINGS ===
STOP_ID = "00001"              # StopAreaCode for Station Sloterdijk
LINE_NUMBER = "22"
DIRECTION = "Muiderpoortstation"
REFRESH_INTERVAL = 30          # seconds between updates

def get_schedule(stop_id):
    url = f"http://v0.ovapi.nl/stopareacode/{stop_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def find_next_bus(schedule, line, direction):
    now = datetime.datetime.now(datetime.timezone.utc)
    next_bus = None

    for _, area_data in schedule.items():
        for _, stop_data in area_data.get("TimingPoints", {}).items():
            for _, vehicle in stop_data.get("Passes", {}).items():
                try:
                    line_num = vehicle.get("LinePublicNumber", "")
                    dest = vehicle.get("DestinationName50", "")
                    target_time = vehicle.get("TargetDepartureTime", "")
                    expected_time = vehicle.get("ExpectedDepartureTime", "")

                    if not target_time or line_num != line or direction.lower() not in dest.lower():
                        continue

                    target_dt = datetime.datetime.fromisoformat(target_time.replace("Z", "+00:00"))
                    expected_dt = (
                        datetime.datetime.fromisoformat(expected_time.replace("Z", "+00:00"))
                        if expected_time else target_dt
                    )

                    if expected_dt > now:
                        delay = int((expected_dt - target_dt).total_seconds() / 60)
                        mins_left = int((expected_dt - now).total_seconds() / 60)

                        # sla de eerstvolgende bus op (de vroegste)
                        if next_bus is None or expected_dt < next_bus["expected"]:
                            next_bus = {
                                "target": target_dt,
                                "expected": expected_dt,
                                "delay": delay,
                                "mins_left": mins_left
                            }
                except Exception:
                    continue

    return next_bus

def show_next_bus():
    while True:
        os.system("clear")
        print(f"🚌  Eerstvolgende buslijn {LINE_NUMBER} → {DIRECTION}")
        print("📍  Halte: Station Sloterdijk (StopArea 00001)")
        print("⏱  Laatste update:", datetime.datetime.now().strftime("%H:%M:%S"))
        print("-" * 60)

        try:
            schedule = get_schedule(STOP_ID)
            next_bus = find_next_bus(schedule, LINE_NUMBER, DIRECTION)

            if not next_bus:
                print("⚠️  Geen aankomende bus gevonden.")
            else:
                planned = next_bus["target"].astimezone().strftime("%H:%M")
                eta = next_bus["expected"].astimezone().strftime("%H:%M")
                delay = next_bus["delay"]
                mins = next_bus["mins_left"]

                if delay > 0:
                    delay_str = f"(+{delay} min vertraging)"
                elif delay < 0:
                    delay_str = f"({abs(delay)} min te vroeg)"
                else:
                    delay_str = "(op tijd)"

                print(f"🕓  Gepland vertrek:  {planned}")
                print(f"⏰  Verwacht vertrek: {eta} {delay_str}")
                print(f"⌛  Over {mins} minuten\n")

        except Exception as e:
            print("❌  Fout bij ophalen data:", e)

        print("-" * 60)
        print(f"Volgende update over {REFRESH_INTERVAL} seconden…")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    show_next_bus()
