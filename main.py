from machine import I2C, Pin
import time
from ssd1306 import SSD1306
from mpu6050_temp import MPU6050
from AHT20 import AHT20
from bmp280 import BMP280
from bmp180 import BMP180
import onewire
import ds18x20

# --- Configurações do Barramento I2C 1 (Sensores Originais) ---
SDA1_PIN = 18
SCL1_PIN = 19
i2c1 = I2C(1, sda=Pin(SDA1_PIN), scl=Pin(SCL1_PIN), freq=100000)

# --- Configurações do Barramento I2C 0 (BMP180 e Display OLED) ---
SDA0_PIN = 16
SCL0_PIN = 17
i2c0 = I2C(0, sda=Pin(SDA0_PIN), scl=Pin(SCL0_PIN), freq=100000)

# --- Configuração do DS18x20 (OneWire no pino 2) ---
ds_pin = Pin(2, Pin.IN)
ds = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds.scan()
if not roms:
    print("ERRO: Nenhum sensor DS18x20 encontrado no pino 2!")
else:
    print(f"Sensor DS18x20 encontrado: {roms}")

print("=== Inicializando Sensores nos Barramentos I2C ===")

# --- Barramento 1 ---
print(f"\n--- Barramento I2C 1 (SDA={SDA1_PIN}, SCL={SCL1_PIN}) ---")
devices1 = i2c1.scan()
if not devices1:
    print("ERRO: Nenhum dispositivo encontrado no barramento 1!")
else:
    print(f"Dispositivos encontrados: {[hex(d) for d in devices1]}")
    mpu_sensor = MPU6050(i2c1)
    aht_sensor = AHT20(i2c1)
    bmp280_sensor = BMP280(i2c1)

# --- Barramento 0 ---
print(f"\n--- Barramento I2C 0 (SDA={SDA0_PIN}, SCL={SCL0_PIN}) ---")
devices0 = i2c0.scan()
if not devices0:
    print("ERRO: Nenhum dispositivo encontrado no barramento 0!")
else:
    print(f"Dispositivos encontrados: {[hex(d) for d in devices0]}")
    bmp180_sensor = BMP180(i2c0)
    oled = SSD1306(128, 64, i2c0)

# --- Loop de Leitura ---
print("\nLendo dados dos sensores... (pressione CTRL+C para parar)")
screen = 0  # Variável para alternar entre telas

while True:
    try:
        print("-" * 25)

        # Leitura dos sensores no barramento 1
        tempA = mpu_sensor.get_temperature()
        tempB, umidA = aht_sensor.get_data()
        tempC, pressA = bmp280_sensor.get_data()

        # Leitura do sensor no barramento 0
        tempD, pressB = bmp180_sensor.get_data()

        # Leitura do DS18x20 (OneWire)
        tempE = None
        if roms:
            ds.convert_temp()
            time.sleep_ms(750)  # Delay necessário para conversão
            tempE = ds.read_temp(roms[0])  # Lê o primeiro sensor encontrado

        # Exibe no console
        print("--- Dados do Barramento 1 ---")
        if tempA is not None:
            print(f"TempA = {tempA:.2f} °C")
        if tempB is not None and umidA is not None:
            print(f"TempB = {tempB:.2f} °C, UmidA = {umidA:.2f} %")
        if tempC is not None and pressA is not None:
            print(f"TempC = {tempC:.2f} °C, PressA = {pressA:.2f} hPa")
        print("--- Dados do Barramento 0 ---")
        if tempD is not None and pressB is not None:
            print(f"TempD = {tempD:.2f} °C, PressB = {pressB:.2f} hPa")
        print("--- Dados do DS18x20 ---")
        if tempE is not None:
            print(f"TempE = {tempE:.2f} °C")
        else:
            print("ERRO: Falha na leitura do DS18x20")

        # Exibe no display OLED
        oled.fill(0)
        if screen == 0:
            # Primeira Tela: Todas as Temperaturas
            oled.text(f"TempA: {tempA:.1f} C" if tempA is not None else "TempA: --.- C", 0, 0)
            oled.text(f"TempB: {tempB:.1f} C" if tempB is not None else "TempB: --.- C", 0, 10)
            oled.text(f"TempC: {tempC:.1f} C" if tempC is not None else "TempC: --.- C", 0, 20)
            oled.text(f"TempD: {tempD:.1f} C" if tempD is not None else "TempD: --.- C", 0, 30)
            oled.text(f"TempE: {tempE:.1f} C" if tempE is not None else "TempE: --.- C", 0, 40)
        else:
            # Segunda Tela: Pressão e Umidade
            oled.text(f"PressA: {pressA:.1f} hPa" if pressA is not None else "PressA: ----.- hPa", 0, 0)
            oled.text(f"PressB: {pressB:.1f} hPa" if pressB is not None else "PressB: ----.- hPa", 0, 10)
            oled.text(f"UmidA: {umidA:.1f} %" if umidA is not None else "UmidA: ----.- %", 0, 20)
        oled.show()
        screen = 1 - screen  # Alterna entre as telas

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        break

    time.sleep(5)  # Intervalo para alternar as telas
