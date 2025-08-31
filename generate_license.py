import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import subprocess

SECRET = b"y8$Gv9!qX2p#Rm4@fL7&Zs6^Bw1*Tj0u"  # 32 bytes

def get_cpu_id():
    """Return CPU ID as unique machine identifier."""
    try:
        if os.name == "nt":
            # Windows
            cmd = "wmic cpu get processorid"
            cpu_id = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
        else:
            # Linux / macOS
            cmd = "lscpu | grep 'Serial\|ID'"
            cpu_id = subprocess.check_output(cmd, shell=True).decode().strip().split()[-1]
        return cpu_id
    except Exception as e:
        print("Could not get CPU ID, using fallback.")
        return "fallback_machine_id"

machine_id = get_cpu_id()
license_key = hashlib.sha256(machine_id.encode() + SECRET).hexdigest()

# create JSON
license_data = json.dumps({"machine_id": machine_id, "license_key": license_key})

# encrypt
cipher = AES.new(SECRET, AES.MODE_CBC)
ct_bytes = cipher.encrypt(pad(license_data.encode(), AES.block_size))
iv = base64.b64encode(cipher.iv).decode('utf-8')
ct = base64.b64encode(ct_bytes).decode('utf-8')

# save encrypted license.json
with open("license.json", "w") as f:
    json.dump({"iv": iv, "data": ct}, f, indent=4)

print("Encrypted license generated for this PC.")
