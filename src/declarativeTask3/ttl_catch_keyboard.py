import keyboard  # using module keyboard
from declarativeTask3.config import ttl_characters


def wait_for_ttl_keyboard():
    while True:
        try:
            if any([keyboard.is_pressed(ttl_char) for ttl_char in ttl_characters]):
                print('You entered the TTL!')
                break  # finishing the loop
            else:
                pass
        except:
            break
    return None
