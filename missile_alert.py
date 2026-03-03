# /// script
# dependencies = ["requests"]
# ///

import requests
import time
import os
import json
import argparse
from datetime import datetime, timedelta

SLACK_TOKEN = os.environ["SLACK_TOKEN"]

OREF_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
SLACK_PROFILE_SET_URL = "https://slack.com/api/users.profile.set"
SLACK_PROFILE_GET_URL = "https://slack.com/api/users.profile.get"

OREF_HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest",
}

ALERT_STATUS = {
    "status_text": "Taking cover, brb 🏃💨",
    "status_emoji": ":rocket:",
    "status_expiration": 0,
}


def get_current_status():
    resp = requests.get(
        SLACK_PROFILE_GET_URL,
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        timeout=5,
    )
    data = resp.json()
    if not data.get("ok"):
        print(f"Slack error (get): {data.get('error')}")
        return {"status_text": "", "status_emoji": "", "status_expiration": 0}
    profile = data["profile"]
    return {
        "status_text": profile.get("status_text", ""),
        "status_emoji": profile.get("status_emoji", ""),
        "status_expiration": profile.get("status_expiration", 0),
    }


def set_slack_status(profile):
    resp = requests.post(
        SLACK_PROFILE_SET_URL,
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"profile": profile},
        timeout=5,
    )
    data = resp.json()
    if not data.get("ok"):
        print(f"Slack error (set): {data.get('error')}")


def check_alerts():
    try:
        resp = requests.get(OREF_URL, headers=OREF_HEADERS, timeout=5)
        text = resp.content.decode("utf-8-sig").strip()
        if text and text != "null":
            data = json.loads(text)
            return data.get("data", [])
    except Exception as e:
        print(f"Oref error: {e}")
    return []


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--test-alert", action="store_true", help="Set alert status and exit")
    group.add_argument("--test-clear", action="store_true", help="Restore previous status and exit")
    parser.add_argument("--city", help="Only trigger for alerts in this city (Hebrew name, e.g. תל אביב)")
    args = parser.parse_args()

    if args.test_alert:
        print("🚨 Testing alert status...")
        set_slack_status(ALERT_STATUS)
        print("Done — check your Slack status")
        return

    if args.test_clear:
        print("✅ Testing clear status...")
        set_slack_status({"status_text": "", "status_emoji": "", "status_expiration": 0})
        print("Done — check your Slack status")
        return

    CLEAR_DELAY = timedelta(minutes=10)

    alert_active = False
    previous_status = None
    last_alert_time = None
    print("Monitoring for Tseva Adom alerts... (Ctrl+C to stop)")

    while True:
        alerts = check_alerts()

        if args.city:
            alerts = [a for a in alerts if args.city in a]

        if alerts:
            if not alert_active:
                print(f"🚨 ALERT: {', '.join(alerts)}")
                previous_status = get_current_status()
                set_slack_status(ALERT_STATUS)
                alert_active = True
            last_alert_time = datetime.now()

        elif alert_active and last_alert_time:
            elapsed = datetime.now() - last_alert_time
            remaining = CLEAR_DELAY - elapsed
            if remaining.total_seconds() <= 0:
                print("✅ All clear — restoring previous status")
                set_slack_status(previous_status or {"status_text": "", "status_emoji": "", "status_expiration": 0})
                alert_active = False
                previous_status = None
                last_alert_time = None
            else:
                print(f"⏳ Waiting to clear... {int(remaining.total_seconds())}s remaining")

        time.sleep(5)


if __name__ == "__main__":
    main()
