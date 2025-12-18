from machine import Pin, SoftI2C
import time

print("=== SCAN SoftI2C ===")

i2c = SoftI2C(
    sda=Pin(14),
    scl=Pin(15),
    freq=400000
)

time.sleep(1)

devices = i2c.scan()
print("Dispositivos encontrados:", devices)
