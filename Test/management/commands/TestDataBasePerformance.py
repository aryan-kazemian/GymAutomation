import time
import random
from datetime import datetime
from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Create, patch, and optionally delete users, shifts, membership types, person roles, people, and members for testing.'

    API_BASE = 'http://127.0.0.1:8000/api/dynamic/'

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stdout.write(f"[{now}] {msg}")

    def create_entities(self, session, entity_name, count, payload_func):
        self.log(f"Starting creation of {count} {entity_name}...")
        ids = []
        headers = {'Content-Type': 'application/json'}
        for i in range(1, count + 1):
            payload = payload_func(i)
            try:
                response = session.post(f"{self.API_BASE}?action={entity_name}", json=payload, headers=headers, timeout=10)
                if response.status_code == 201:
                    entity_id = response.json().get('id')
                    if entity_id is not None:
                        ids.append(entity_id)
                        self.log(f"Created {entity_name} with ID {entity_id}")
                    else:
                        self.stdout.write(self.style.ERROR(f"No ID returned when creating {entity_name} #{i}. Response: {response.text}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to create {entity_name} #{i}. Status: {response.status_code} Response: {response.text}"))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception creating {entity_name} #{i}: {str(e)}"))
        self.log(f"Finished creating {count} {entity_name}. Created IDs count: {len(ids)}")
        return ids

    def patch_entities(self, session, entity_name, ids, patch_count, patch_func):
        if patch_count <= 0 or not ids:
            self.log(f"No patching for {entity_name}.")
            return

        self.log(f"Starting patch of {patch_count} {entity_name}...")
        headers = {'Content-Type': 'application/json'}

        if patch_count <= len(ids):
            chosen_ids = random.sample(ids, patch_count)
        else:
            repeats = (patch_count // len(ids)) + 1
            extended_list = ids * repeats
            chosen_ids = extended_list[:patch_count]

        for idx, entity_id in enumerate(chosen_ids, 1):
            payload = patch_func(idx, entity_id)
            try:
                response = session.patch(f"{self.API_BASE}?action={entity_name}&id={entity_id}", json=payload, headers=headers, timeout=10)
                if response.status_code not in (200, 201):
                    self.stdout.write(self.style.ERROR(f"Failed to patch {entity_name} ID {entity_id}. Status: {response.status_code} Response: {response.text}"))
                else:
                    self.log(f"Patched {entity_name} with ID {entity_id}")
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception patching {entity_name} ID {entity_id}: {str(e)}"))
        self.log(f"Finished patching {patch_count} {entity_name}.")

    def delete_entities(self, session, entity_name, ids):
        if not ids:
            self.log(f"No deletion for {entity_name}.")
            return

        self.log(f"Starting deletion of {len(ids)} {entity_name}...")
        start_time = time.time()
        deleted_count = 0
        for entity_id in ids:
            try:
                response = session.delete(f"{self.API_BASE}?action={entity_name}&id={entity_id}", timeout=10)
                if response.status_code in (200, 204):
                    self.log(f"Deleted {entity_name} with ID {entity_id}")
                    deleted_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to delete {entity_name} ID {entity_id}. Status: {response.status_code} Response: {response.text}"))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Exception deleting {entity_name} ID {entity_id}: {str(e)}"))
        elapsed = time.time() - start_time
        self.log(f"Finished deleting {deleted_count} out of {len(ids)} {entity_name} in {elapsed:.2f} seconds.")

    def handle(self, *args, **options):
        self.log("Test create/patch started.")
        summary = {}

        with requests.Session() as session:

            # ----------- USERS -----------
            user_count = input("How many users to create? (default 10): ") or "10"
            user_count = int(user_count)
            start = time.time()
            users = self.create_entities(session, "user", user_count, lambda i: {
                "username": f"test_user_{i}",
                "password": "test_password",
                "is_admin": False,
                "shift": None,
                "is_active": True,
            })
            elapsed = time.time() - start
            summary['users_created'] = (len(users), elapsed)

            patch_user_count = input(f"How many users to patch? (default 10): ") or "10"
            patch_user_count = int(patch_user_count)
            start = time.time()
            self.patch_entities(session, "user", users, patch_user_count, lambda idx, eid: {
                "username": f"patched_user_{idx}",
                "password": "patched_password",
                "is_active": True,
            })
            elapsed = time.time() - start
            summary['users_patched'] = (patch_user_count, elapsed)

            # ----------- SHIFTS -----------
            shift_count = input("How many shifts to create? (default 10): ") or "10"
            shift_count = int(shift_count)
            start = time.time()
            shifts = self.create_entities(session, "shift", shift_count, lambda i: {
                "shift_desc": f"Description for Shift {i}"
            })
            elapsed = time.time() - start
            summary['shifts_created'] = (len(shifts), elapsed)

            patch_shift_count = input(f"How many shifts to patch? (default 10): ") or "10"
            patch_shift_count = int(patch_shift_count)
            start = time.time()
            self.patch_entities(session, "shift", shifts, patch_shift_count, lambda idx, eid: {
                "shift_desc": f"Patched Description for Shift {idx}"
            })
            elapsed = time.time() - start
            summary['shifts_patched'] = (patch_shift_count, elapsed)

            # ----------- MEMBERSHIP TYPES -----------
            membership_type_count = input("How many membership types to create? (default 10): ") or "10"
            membership_type_count = int(membership_type_count)
            start = time.time()
            membership_types = self.create_entities(session, "membership_type", membership_type_count, lambda i: {
                "membership_type_desc": f"Description for MembershipType {i}"
            })
            elapsed = time.time() - start
            summary['membership_types_created'] = (len(membership_types), elapsed)

            patch_membership_type_count = input(f"How many membership types to patch? (default 10): ") or "10"
            patch_membership_type_count = int(patch_membership_type_count)
            start = time.time()
            self.patch_entities(session, "membership_type", membership_types, patch_membership_type_count, lambda idx, eid: {
                "membership_type_desc": f"Patched Description for MembershipType {idx}"
            })
            elapsed = time.time() - start
            summary['membership_types_patched'] = (patch_membership_type_count, elapsed)

            # ----------- PERSON ROLES -----------
            role_count = input("How many person roles to create? (default 10): ") or "10"
            role_count = int(role_count)
            start = time.time()
            person_roles = self.create_entities(session, "role", role_count, lambda i: {
                "role_desc": f"Role description {i}"
            })
            elapsed = time.time() - start
            summary['person_roles_created'] = (len(person_roles), elapsed)

            patch_role_count = input(f"How many person roles to patch? (default 10): ") or "10"
            patch_role_count = int(patch_role_count)
            start = time.time()
            self.patch_entities(session, "role", person_roles, patch_role_count, lambda idx, eid: {
                "role_desc": f"Patched role description {idx}"
            })
            elapsed = time.time() - start
            summary['person_roles_patched'] = (patch_role_count, elapsed)

            # ----------- PEOPLE -----------
            person_count = input("How many people to create? (default 10): ") or "10"
            person_count = int(person_count)
            start = time.time()
            people = self.create_entities(session, "person", person_count, lambda i: {
                "first_name": f"FirstName{i}",
                "last_name": f"LastName{i}",
                "full_name": f"FirstName{i} LastName{i}",
                "father_name": f"Father{i}",
                "gender": random.choice(['M', 'F', 'O']),
                "national_code": f"NC{i:05d}",
                "nidentity": f"ID{i:05d}",
                "birth_date": "1990-01-01",
                "tel": f"021-123456{i}",
                "mobile": f"0912-34567{i}",
                "email": f"user{i}@example.com",
                "education": "Bachelor",
                "job": "Developer",
                "has_insurance": False,
                "insurance_no": None,
                "ins_start_date": None,
                "ins_end_date": None,
                "address": f"Address {i}",
                "has_parrent": False,
                "team_name": f"Team {i}",
                "shift": None,
                "user": None,
                "modifier": "System",
                "modification_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            elapsed = time.time() - start
            summary['people_created'] = (len(people), elapsed)

            patch_person_count = input("How many people to patch? (default 10): ") or "10"
            patch_person_count = int(patch_person_count)
            start = time.time()
            self.patch_entities(session, "person", people, patch_person_count, lambda idx, eid: {
                "first_name": f"PatchedFirstName{idx}",
                "last_name": f"PatchedLastName{idx}",
                "full_name": f"PatchedFirstName{idx} PatchedLastName{idx}",
                "modifier": "PatchedSystem",
            })
            elapsed = time.time() - start
            summary['people_patched'] = (patch_person_count, elapsed)

            # ----------- MEMBERS -----------
            member_count = input("How many members to create? (default 10): ") or "10"
            member_count = int(member_count)
            start = time.time()
            members = self.create_entities(session, "member", member_count, lambda i: {
                "membership_type": None,
                "card_no": f"CARD{i:05d}",
                "couch_id": None,
                "person": None,
                "role": None,
                "user": None,
                "shift": None,
                "is_black_list": False,
                "box_radif_no": f"BRN{i:05d}",
                "has_finger": True,
                "membership_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "modifier": "System",
                "modification_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "is_family": False,
                "max_debit": 100.00,
                "salary": 1000.00,
                "session_left": 10,
                "end_date": "2025-12-31",
                "sport": "Tennis",
                "price": "200"
            })
            elapsed = time.time() - start
            summary['members_created'] = (len(members), elapsed)

            patch_member_count = input("How many members to patch? (default 10): ") or "10"
            patch_member_count = int(patch_member_count)
            start = time.time()
            self.patch_entities(session, "member", members, patch_member_count, lambda idx, eid: {
                "card_no": f"PatchedCard{idx:05d}",
                "is_black_list": True,
                "modifier": "PatchedSystem",
            })
            elapsed = time.time() - start
            summary['members_patched'] = (patch_member_count, elapsed)

            # ----------- ASK TO DELETE -----------
            delete_all = input("Do you want to delete all created data? (y/n, default n): ") or "n"
            if delete_all.lower() == 'y':
                start = time.time()
                self.delete_entities(session, "member", members)
                self.delete_entities(session, "person", people)
                self.delete_entities(session, "role", person_roles)
                self.delete_entities(session, "membership_type", membership_types)
                self.delete_entities(session, "shift", shifts)
                self.delete_entities(session, "user", users)
                elapsed = time.time() - start
                summary['all_deleted'] = elapsed
            else:
                self.log("Skipping deletion of entities.")

        # Summary output
        self.stdout.write("\n===== SUMMARY =====")
        for key, val in summary.items():
            if isinstance(val, tuple):
                self.stdout.write(f"{key.replace('_', ' ').title()}: {val[0]} in {val[1]:.2f} sec")
            else:
                self.stdout.write(f"{key.replace('_', ' ').title()}: {val}")

        self.log("Test create/patch finished.")
