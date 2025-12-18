from mpu6050_temp import SoftI2C, MPU6050
from bmp280 import BMP280
from AHT20 import AHT20
from machine import Pin
from dht import DHT11, DHT22
from ntc import NTC
import time

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================
I2C_SCL = 13
I2C_SDA = 12

DHT22_PIN = 16
DHT11_PIN = 17
NTC_ADC   = 28

BMP_SAMPLES = 10
BMP_SAMPLE_DELAY = 0.2
LOOP_DELAY = 1

# =====================================================
# I2C
# =====================================================
def init_i2c():
    print("Inicializando barramento I2C...")
    return SoftI2C(scl_pin=I2C_SCL, sda_pin=I2C_SDA)

# =====================================================
# FUNÇÕES DE INICIALIZAÇÃO
# =====================================================
def init_mpu6050(i2c):
    for _ in range(3):
        try:
            mpu = MPU6050(i2c)
            if mpu.is_ready:
                print("MPU6050 OK")
                return mpu
        except:
            time.sleep(1)
    print("MPU6050 ausente")
    return None


def init_bmp280(i2c):
    try:
        bmp = BMP280(i2c)
        print("BMP280 OK" if bmp.is_ready else "BMP280 não respondeu")
        return bmp if bmp.is_ready else None
    except:
        print("BMP280 ausente")
        return None


def init_aht20(i2c):
    try:
        aht = AHT20(i2c)
        print("AHT20 OK" if aht.is_ready else "AHT20 não respondeu")
        return aht if aht.is_ready else None
    except:
        print("AHT20 ausente")
        return None


def init_ntc():
    try:
        ntc = NTC(NTC_ADC)
        print("NTC OK")
        return ntc
    except:
        print("NTC ausente")
        return None


def init_dht():
    dht22 = dht11 = None

    try:
        dht22 = DHT22(Pin(DHT22_PIN))
        print("DHT22 OK")
    except:
        print("DHT22 ausente")

    try:
        dht11 = DHT11(Pin(DHT11_PIN))
        print("DHT11 OK")
    except:
        print("DHT11 ausente")

    return dht22, dht11

# =====================================================
# FUNÇÕES DE LEITURA
# =====================================================
def read_mpu(mpu):
    try:
        t = mpu.get_temperature()
        if t is not None:
            print(f"MPU6050  : {t:.2f} °C")
    except:
        pass


def read_bmp(bmp):
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


def read_aht(aht):
    try:
        t, h = aht.get_data()
        if -40 <= t <= 85 and 1 <= h <= 100:
            print(f"AHT20    : {t:.2f} °C | {h:.2f} %")
    except:
        pass


def read_ntc(ntc):
    try:
        t = ntc.get_temperature()
        if -40 <= t <= 125:
            print(f"NTC      : {t:.2f} °C")
    except:
        pass


def read_dht(sensor, label):
    try:
        sensor.measure()
        print(f"{label:<9}: {sensor.temperature():.2f} °C | {sensor.humidity():.2f} %")
    except:
        pass

# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================
def main():
    i2c = init_i2c()
    time.sleep(2)

    mpu = init_mpu6050(i2c)
    bmp = init_bmp280(i2c)
    aht = init_aht20(i2c)
    ntc = init_ntc()

    time.sleep(2)
    dht22, dht11 = init_dht()

    print("\nLeitura contínua (atualização a cada 30s)\n")

    while True:
        if mpu:
            read_mpu(mpu)

        if bmp:
            read_bmp(bmp)

        if aht:
            read_aht(aht)

        if ntc:
            read_ntc(ntc)

        if dht22:
            read_dht(dht22, "DHT22")

        time.sleep(2)

        if dht11:
            read_dht(dht11, "DHT11")

        print("-" * 40)
        time.sleep(LOOP_DELAY)


if __name__ == "__main__":
    main()
