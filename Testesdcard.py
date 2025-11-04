# datalogger_rtc.py - Logs date and time to SD Card with safe eject button
import os
import machine
import time
from sdcard import SDCard

# --- Hardware Configuration ---

# Onboard LED for visual feedback
led = machine.Pin("LED", machine.Pin.OUT)

# Safe Eject Button on GP3
# Connection: One button pin -> GP3, other pin -> 3V3 (Pin 36)
eject_button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)

# SPI(1) Hardware Configuration - Physical Pins 14, 15, 16, 17
spi = machine.SPI(1,
                  baudrate=1000000,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))
cs = machine.Pin(13, machine.Pin.OUT)

# --- Initialization ---

print("Initializing logging system...")

# Mount SD card
try:
    sd = SDCard(spi, cs)
    os.mount(sd, '/sd')
    print("✓ SD card mounted successfully.")
except Exception as e:
    print(f"✗ Critical failure mounting SD card: {e}")
    print("Program will be terminated.")
    raise

# Initialize Real-Time Clock (RTC)
rtc = machine.RTC()

# IMPORTANT: On first run, uncomment the line below
# and adjust to current date and time to set the clock.
# Format: (year, month, day, weekday, hour, minute, second, microsecond)
# Example for August 25, 2025, 18:13:00 (Monday = 0)
# rtc.datetime((2025, 8, 25, 0, 18, 13, 0, 0))

# Define log file name
log_file_path = '/sd/timelog3.csv'

# Create file with header if it doesn't exist
try:
    with open(log_file_path, 'r') as f:
        pass # File already exists, do nothing
    print(f"✓ Using existing log file: {log_file_path}")
except OSError:
    # File doesn't exist, create it with header
    with open(log_file_path, 'w') as f:
        f.write("Timestamp\n")
    print(f"✓ New log file created: {log_file_path}")

print("\n--- LOGGING STARTED ---")
print("Press button on GP3 to safely unmount card.")

# --- Main Loop ---
while True:
    # Check if eject button was pressed
    if eject_button.value() == 1:
        print("\nEject button pressed. Finalizing...")
        break

    # Get current date and time from RTC
    current_time = rtc.datetime()
    
    # Format date and time as friendly string
    timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[0], current_time[1], current_time[2],
        current_time[4], current_time[5], current_time[6]
    )

    # Open file in append mode and save new line
    try:
        with open(log_file_path, 'a') as f:
            f.write(f"{timestamp_str}\n")
        
        # Blink LED quickly to indicate record was saved
        led.on()
        time.sleep_ms(50)
        led.off()
        
        print(f"Record saved: {timestamp_str}")

    except Exception as e:
        print(f"✗ Error saving to file: {e}")

    # Wait 5 seconds for next record
    time.sleep(5)

# --- Safe Shutdown and Ejection ---
print("\nUnmounting SD card filesystem...")
try:
    os.umount('/sd')
    print("✓ SD card safely unmounted!")
    
    # Blink LED 5 times to signal safe card removal
    for _ in range(5):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)
        
except Exception as e:
    print(f"✗ Error unmounting SD card: {e}")

print("Program terminated. Safe to remove card.")