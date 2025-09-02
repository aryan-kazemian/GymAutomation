import time
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'Create persons with sequential national_code and test filtering speed.'

    API_BASE = 'http://127.0.0.1:8000/api/dynamic/'   # DynamicAPIView (persons)

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stdout.write(f"[{now}] {msg}")

    # ---------- Person creation / filtering ----------

    def create_persons(self, session, count):
        self.log(f"Starting creation of {count} persons...")
        created_codes = []
        headers = {'Content-Type': 'application/json'}

        for i in range(1, count + 1):
            national_code = f"{i:010d}"  # 10-digit code

            # Generate a birth_date within last 50 years
            birth_date = (datetime.now() - timedelta(days=random.randint(18 * 365, 50 * 365))).date()

            payload = {
                "first_name": random.choice(["Ali", "Sara", "John", "Mary", "Omid", "Lina"]),
                "last_name": random.choice(["Smith", "Johnson", "Karimi", "Rahimi", "Lee", "Chen"]),
                "national_code": national_code,
                "father_name": random.choice(["Reza", "Hossein", "David", "Michael", "Hassan", "Robert"]),
                "birth_date": birth_date.isoformat(),  # YYYY-MM-DD
                "email": f"user{i}@example.com",
                "phone": f"021{random.randint(1000000, 9999999)}",
                "mobile": f"09{random.randint(100000000, 999999999)}",
                "gender": random.choice(["F", "M"]),
                "address": f"Street {random.randint(1, 100)}, City",
                "postal_code": f"{random.randint(10000, 99999)}"
            }

            try:
                response = session.post(f"{self.API_BASE}?action=person", json=payload, headers=headers, timeout=15)
                if response.status_code == 201:
                    created_codes.append(national_code)
                    self.log(f"Created person with national_code {national_code}")
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to create person #{i} national_code {national_code}. "
                        f"Status: {response.status_code} Response: {response.text}"
                    ))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception creating person #{i} national_code {national_code}: {str(e)}"))

        self.log(f"Finished creating {len(created_codes)} persons.")
        return created_codes

    def filter_persons(self, session, codes, filter_count):
        self.log(f"Starting {filter_count} person filters...")

        found_count = 0
        start_time = time.time()

        max_code_int = len(codes)

        for i in range(filter_count):
            # 70% chance to pick an existing national_code
            if random.random() < 0.7 and codes:
                national_code = random.choice(codes)
            else:
                # Generate a random non-existing national_code
                national_code = f"{random.randint(max_code_int + 1, max_code_int + 1000):010d}"

            try:
                resp = session.get(f"{self.API_BASE}?action=person&national_code={national_code}", timeout=10)
                if resp.status_code == 200:
                    data = resp.json() if resp.content else {}
                    items = data.get('items', []) if isinstance(data, dict) else []
                    if isinstance(items, list) and len(items) > 0:
                        found_count += 1
                        self.log(f"Filter {i+1}: Found person with national_code {national_code}")
                    else:
                        self.log(f"Filter {i+1}: No person found with national_code {national_code}")
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Filter {i+1}: Unexpected status {resp.status_code} for national_code {national_code}. Resp: {resp.text}"
                    ))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception during filter {i+1} for national_code {national_code}: {str(e)}"))

        elapsed = time.time() - start_time
        self.log(f"Finished filtering {filter_count} persons.")
        return found_count, elapsed

    # ---------- entrypoint ----------

    def handle(self, *args, **options):
        self.log("Person creation and filter test started.")
        summary = {}

        with requests.Session() as session:
            # Inputs
            person_count_str = input("How many persons do you want to create? (default 10): ") or "10"
            filter_count_str = input("How many filter queries do you want to perform? (default 10): ") or "10"
            try:
                person_count = int(person_count_str)
                filter_count = int(filter_count_str)
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid input. Please enter integers."))
                return

            # Create persons
            codes = self.create_persons(session, person_count)
            summary['persons_created'] = len(codes)

            # Filter
            found_count, elapsed = self.filter_persons(session, codes, filter_count)
            summary['filters_performed'] = filter_count
            summary['filters_found'] = found_count
            summary['filters_time'] = elapsed
            summary['filters_avg_time_ms'] = (elapsed / filter_count * 1000) if filter_count else 0

        self.stdout.write("\n===== SUMMARY =====")
        self.stdout.write(f"Persons created: {summary['persons_created']}")
        self.stdout.write(f"Filters performed: {summary['filters_performed']}")
        self.stdout.write(f"Filters found: {summary['filters_found']}")
        self.stdout.write(f"Total filtering time: {summary['filters_time']:.2f} sec")
        self.stdout.write(f"Average filtering time per query: {summary['filters_avg_time_ms']:.2f} ms")

        self.log("Person creation and filter test finished.")
