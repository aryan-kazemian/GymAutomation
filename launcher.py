import os
import sys
import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import subprocess

SECRET = b"y8$Gv9!qX2p#Rm4@fL7&Zs6^Bw1*Tj0u"

def get_cpu_id():
    try:
        if os.name == "nt":
            cmd = "wmic cpu get processorid"
            cpu_id = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
        else:
            cmd = "lscpu | grep 'Serial\|ID'"
            cpu_id = subprocess.check_output(cmd, shell=True).decode().strip().split()[-1]
        return cpu_id
    except:
        return "fallback_machine_id"

with open("license.json", "r") as f:
    lic = json.load(f)

iv = base64.b64decode(lic["iv"])
ct = base64.b64decode(lic["data"])

cipher = AES.new(SECRET, AES.MODE_CBC, iv)
decrypted = unpad(cipher.decrypt(ct), AES.block_size)
license_data = json.loads(decrypted)

machine_id = get_cpu_id()
expected_key = hashlib.sha256(machine_id.encode() + SECRET).hexdigest()

if license_data["license_key"] != expected_key:
    print("Invalid license. Exiting.")
    sys.exit(1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GymAutomation.settings")
from django.core.management import execute_from_command_line
execute_from_command_line([sys.argv[0], "runserver", "0.0.0.0:8000", "--noreload"])
