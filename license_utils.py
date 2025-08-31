import uuid

def get_machine_id():
    """
    Returns a unique identifier for this machine.
    Uses the MAC address of the first network interface.
    """
    return str(uuid.getnode())
