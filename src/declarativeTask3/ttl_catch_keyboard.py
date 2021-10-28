import keyboard
from declarativeTask3.config import ttl_characters, min_delay_between_two_ttls, interval_between_ttl_checks


def wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp=None):
    if last_ttl_timestamp is None:
        pass
    else:
        # Too short amount of time between two TTLs expected
        while exp.clock.time - last_ttl_timestamp > min_delay_between_two_ttls:
            exp.clock.wait(interval_between_ttl_checks)

    while True:
        if any([keyboard.is_pressed(ttl_char) for ttl_char in ttl_characters]):
            ttl_timestamp = exp.clock.time
            print(f'TTL received at {ttl_timestamp} ms')
            exp.add_experiment_info(f'TTL_RECEIVED_timing_{ttl_timestamp}')
            return ttl_timestamp
