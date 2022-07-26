import keyboard
import time
from declarativeTask3.config import ttl_characters

previous_ttl_timestamp = None

while True:
    if any([keyboard.is_pressed(ttl_char) for ttl_char in ttl_characters]):
        ttl_timestamp = time.time()

        if previous_ttl_timestamp is not None:
            ttl_interval  = ttl_timestamp - previous_ttl_timestamp
            print(f'interval between TTL is {ttl_interval} s')
        previous_ttl_timestamp = ttl_timestamp
        time.sleep(.5)
