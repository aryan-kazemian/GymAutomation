from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import serial
import time

PORT = "COM3"
BAUDRATE = 9600

uid_to_user = {
    "936C4EA9": "Alice",
    "11223344": "Bob",
    # Add more users here
}

REQUEST_CMD = bytes.fromhex('02 00 02 31 52 61')
ANTICOLL_CMD = bytes.fromhex('02 00 02 32 93 a3')

def send_identification_event(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "identification_group",  # group name in your consumer
        {
            "type": "identification_event",  # consumer handler
            "data": data,
        }
    )

def send_error_event(error_message):
    send_identification_event({"error": error_message})

def send_command(ser, cmd, label):
    print(f"[>] Sent ({label}): {cmd.hex()}")
    ser.write(cmd)
    time.sleep(0.2)
    resp = ser.read_all()
    print(f"[<] Received ({label}): {resp.hex()} | ASCII: {resp.decode(errors='ignore')}")
    return resp

def extract_uid(response):
    if len(response) >= 5:
        uid_bytes = response[-5:-1]
        return ''.join(f'{b:02X}' for b in uid_bytes)
    return None

def main():
    ser = None
    while True:
        try:
            if ser is None or not ser.is_open:
                ser = serial.Serial(PORT, BAUDRATE, timeout=1)
                print(f"[+] Connected to {PORT} at {BAUDRATE} baud")
                send_error_event("Device connected successfully")
        except serial.SerialException as e:
            error_msg = f"Serial connection error: {e}"
            print(f"[!] {error_msg}")
            send_error_event(error_msg)
            time.sleep(5)  # wait and retry connection
            continue

        try:
            # continuously scan cards without waiting for user input
            send_command(ser, REQUEST_CMD, "Request Card")
            resp = send_command(ser, ANTICOLL_CMD, "Anti-collision")

            uid = extract_uid(resp)
            if uid:
                print(f"[✔] UID Detected: {uid}")
                user = uid_to_user.get(uid)
                if user:
                    message = f"Welcome, {user}!"
                else:
                    message = f"Unknown card: {uid}"
                send_identification_event({"uid": uid, "message": message})
            else:
                # no card detected, you can send a heartbeat or nothing
                pass

            time.sleep(1)  # small delay between scans

        except serial.SerialException as e:
            error_msg = f"Device communication error: {e}"
            print(f"[!] {error_msg}")
            send_error_event(error_msg)
            ser.close()
            ser = None
            time.sleep(5)  # wait and retry

if __name__ == "__main__":
    main()
