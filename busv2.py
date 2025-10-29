import requests
import datetime
import os
import time

STOP_AREA = "50005050"     # Contactweg
LINE_NUMBER = "22"
DIRECTION = "Muiderpoortstation"
REFRESH_INTERVAL = 30      # seconds

def get_departures():
    url = f"https://api.gvb.nl/api/v1/stop-areas/{STOP_AREA}/departures"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def find_next_bus(data):
    now = datetime.datetime.now()
    next_bus = None

    for dep in data.get("departures", []):
        line = dep.get("linePublicNumber", "")
        dest = dep.get("destinationName", "")
        time_planned = dep.get("plannedDepartureTime")
        time_expected = dep.get("expectedDepartureTime")

        if line != LINE_NUMBER or DIRECTION.lower() not in dest.lower():
            continue

        planned = datetime.datetime.fromisoformat(time_planned.replace("Z", "+00:00"))
        expected = datetime.datetime.fromisoformat(time_expected.replace("Z", "+00:00")) if time_expected else planned
        delay = int((expected - planned).total_seconds() / 60)
        mins = int((expected - datetime.datetime.now(datetime.timezone.utc)).total_seconds() / 60)

        next_bus = {
            "planned": planned,
            "expected": expected,
            "delay": delay,
            "mins": mins
        }
        break

    return next_bus

def main():
    while True:
        os.system("clear")
        print(f"🚌  Eerstvolgende buslijn {LINE_NUMBER} → {DIRECTION}")
        print("📍  Halte: Amsterdam, Contactweg")
        print("⏱  Laatste update:", datetime.datetime.now().strftime("%H:%M:%S"))
        print("-" * 60)

        try:
            data = get_departures()
            bus = find_next_bus(data)

            if not bus:
                print("⚠️  Geen aankomende bus gevonden.")
            else:
                planned = bus["planned"].astimezone().strftime("%H:%M")
                expected = bus["expected"].astimezone().strftime("%H:%M")
                delay = bus["delay"]
                mins = bus["mins"]

                if delay > 0:
                    delay_str = f"(+{delay} min vertraging)"
                elif delay < 0:
                    delay_str = f"({abs(delay)} min te vroeg)"
                else:
                    delay_str = "(op tijd)"

                print(f"🕓  Gepland vertrek:  {planned}")
                print(f"⏰  Verwacht vertrek: {expected} {delay_str}")
                print(f"⌛  Over {mins} minuten\n")

        except Exception as e:
            print("❌  Fout bij ophalen data:", e)

        print("-" * 60)
        print(f"Volgende update over {REFRESH_INTERVAL} seconden…")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
