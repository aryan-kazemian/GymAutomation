import time
import random
from datetime import datetime
from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Create members with sequential card_no and test filtering speed.'

    API_BASE = 'http://127.0.0.1:8000/api/dynamic/'

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stdout.write(f"[{now}] {msg}")

    def create_members(self, session, count):
        self.log(f"Starting creation of {count} members...")
        created_cardnos = []
        headers = {'Content-Type': 'application/json'}

        for i in range(1, count + 1):
            card_no = f"{i:06d}"
            payload = {
                "membership_type": None,
                "card_no": card_no,
                "couch_id": None,
                "person": None,
                "role": None,
                "user": None,
                "shift": None,
                "is_black_list": bool(random.getrandbits(1)),
                "box_radif_no": f"BRN{i:05d}",
                "has_finger": bool(random.getrandbits(1)),
                "membership_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "modifier": "System",
                "modification_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "is_family": bool(random.getrandbits(1)),
                "max_debit": round(random.uniform(50, 200), 2),
                "salary": round(random.uniform(500, 2000), 2),
                "session_left": random.randint(0, 20),
                "end_date": "2025-12-31",
                "sport": random.choice(["Tennis", "Football", "Basketball"]),
                "price": str(random.randint(100, 500))
            }
            try:
                response = session.post(f"{self.API_BASE}?action=member", json=payload, headers=headers, timeout=10)
                if response.status_code == 201:
                    created_cardnos.append(card_no)
                    self.log(f"Created member with card_no {card_no}")
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to create member #{i} with card_no {card_no}. Status: {response.status_code} Response: {response.text}"))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception creating member #{i} with card_no {card_no}: {str(e)}"))

        self.log(f"Finished creating {len(created_cardnos)} members.")
        return created_cardnos

    def filter_members(self, session, cardnos, filter_count):
        self.log(f"Starting {filter_count} member filters...")
        headers = {'Content-Type': 'application/json'}

        found_count = 0
        start_time = time.time()

        max_card_no_int = len(cardnos)

        for i in range(filter_count):
            # Randomly decide to search for existing or non-existing card_no
            if random.random() < 0.7 and cardnos:  # 70% chance to pick an existing card_no
                card_no = random.choice(cardnos)
            else:
                # Generate a random non-existing card_no, e.g. beyond max_card_no_int + 1000
                card_no = f"{random.randint(max_card_no_int + 1, max_card_no_int + 1000):06d}"

            try:
                # Assuming your API supports filtering by card_no via GET query params:
                # If your API is different, adapt accordingly
                resp = session.get(f"{self.API_BASE}?action=member&card_no={card_no}", timeout=10)
                if resp.status_code == 200 and resp.json():
                    found_count += 1
                    self.log(f"Filter {i+1}: Found member with card_no {card_no}")
                else:
                    self.log(f"Filter {i+1}: No member found with card_no {card_no}")
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception during filter {i+1} for card_no {card_no}: {str(e)}"))

        elapsed = time.time() - start_time
        self.log(f"Finished filtering {filter_count} members.")
        return found_count, elapsed

    def handle(self, *args, **options):
        self.log("Member creation and filter test started.")
        summary = {}

        with requests.Session() as session:
            member_count = input("How many members do you want to create? (default 10): ") or "10"
            member_count = int(member_count)

            cardnos = self.create_members(session, member_count)
            summary['members_created'] = (len(cardnos),)

            filter_count = input("How many filter queries do you want to perform? (default 10): ") or "10"
            filter_count = int(filter_count)

            found_count, elapsed = self.filter_members(session, cardnos, filter_count)
            summary['filters_performed'] = (filter_count,)
            summary['filters_found'] = found_count
            summary['filters_time'] = elapsed
            summary['filters_avg_time_ms'] = (elapsed / filter_count * 1000) if filter_count else 0

        self.stdout.write("\n===== SUMMARY =====")
        self.stdout.write(f"Members created: {summary['members_created'][0]}")
        self.stdout.write(f"Filters performed: {summary['filters_performed'][0]}")
        self.stdout.write(f"Filters found: {summary['filters_found']}")
        self.stdout.write(f"Total filtering time: {summary['filters_time']:.2f} sec")
        self.stdout.write(f"Average filtering time per query: {summary['filters_avg_time_ms']:.2f} ms")

        self.log("Member creation and filter test finished.")
