from mpu6050_temp import SoftI2C, MPU6050
from bmp280 import BMP280
from AHT20 import AHT20
from machine import Pin
from dht import DHT11, DHT22
import time

# ================= I2C =================
i2c = SoftI2C(scl_pin=13, sda_pin=12)

print("Inicializando sensores...")
time.sleep(2)

# ================= MPU6050 =================
mpu = None
for _ in range(3):
    try:
        mpu = MPU6050(i2c)
        if mpu.is_ready:
            print("MPU6050 OK")
            break
    except:
        time.sleep(1)

# ================= BMP280 =================
try:
    bmp = BMP280(i2c)
    print("BMP280 OK" if bmp.is_ready else "BMP280 não respondeu")
except:
    bmp = None
    print("BMP280 ausente")

# ================= AHT20 =================
try:
    aht = AHT20(i2c)
    print("AHT20 OK" if aht.is_ready else "AHT20 não respondeu")
except:
    aht = None
    print("AHT20 ausente")

# ================= DHT =================
time.sleep(3)

try:
    dht22 = DHT22(Pin(16))
    print("DHT22 OK")
except:
    dht22 = None
    print("DHT22 ausente")

time.sleep(1)

try:
    dht11 = DHT11(Pin(17))
    print("DHT11 OK")
except:
    dht11 = None
    print("DHT11 ausente")

print("\nLeitura contínua (atualização a cada 30s)")

# ================= CONFIG BMP =================
BMP_SAMPLES = 10
BMP_SAMPLE_DELAY = 0.2

# ================= LOOP =================
while True:

    # MPU6050
    if mpu:
        t = mpu.get_temperature()
        if t is not None:
            print(f"MPU6050  : {t:.2f} °C")

    # BMP280 (média)
    if bmp:
        temps, press = [], []
        for _ in range(BMP_SAMPLES):
            try:
                t, p = bmp.get_data()
                if -20 <= t <= 85 and 300 <= p <= 1100:
                    temps.append(t)
                    press.append(p)
            except:
                pass
            time.sleep(BMP_SAMPLE_DELAY)

        if temps:
            print(f"BMP280   : {sum(temps)/len(temps):.2f} °C | {sum(press)/len(press):.2f} hPa")

    # AHT20
    if aht:
        try:
            t, h = aht.get_data()
            if -40 <= t <= 85 and 1 <= h <= 100:
                print(f"AHT20    : {t:.2f} °C | {h:.2f} %")
        except:
            pass

    # DHT22
    if dht22:
        try:
            dht22.measure()
            print(f"DHT22    : {dht22.temperature():.2f} °C | {dht22.humidity():.2f} %")
        except:
            pass

    time.sleep(2)

    # DHT11
    if dht11:
        try:
            dht11.measure()
            print(f"DHT11    : {dht11.temperature():.2f} °C | {dht11.humidity():.2f} %")
        except:
            pass

    print("-" * 40)
    time.sleep(30)
