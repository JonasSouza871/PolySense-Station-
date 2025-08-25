from machine import I2C, Pin
import time
from ssd1306 import SSD1306

# Importa as bibliotecas de todos os sensores
from mpu6050_temp import MPU6050
from AHT20 import AHT20
from bmp280 import BMP280
from bmp180 import BMP180

# --- Configurações do Barramento I2C 1 (Sensores Originais) ---
SDA1_PIN = 18
SCL1_PIN = 19
i2c1 = I2C(1, sda=Pin(SDA1_PIN), scl=Pin(SCL1_PIN), freq=100000)

# --- Configurações do Barramento I2C 0 (BMP180 e Display OLED) ---
SDA0_PIN = 16
SCL0_PIN = 17
i2c0 = I2C(0, sda=Pin(SDA0_PIN), scl=Pin(SCL0_PIN), freq=100000)

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

        # Exibe no display OLED
        oled.fill(0)

        if screen == 0:
            # **Primeira Tela: TempC, TempD, PressA, TempA, TempB, UmidA**
            oled.text(f"TempC: {tempC:.1f} C", 0, 0)
            oled.text(f"TempD: {tempD:.1f} C", 0, 10)
            oled.text(f"PressA: {pressA:.1f} hPa", 0, 20)
            oled.text(f"TempA: {tempA:.1f} C", 0, 30)
            oled.text(f"TempB: {tempB:.1f} C", 0, 40)
            oled.text(f"UmidA: {umidA:.1f} %", 0, 50)
        else:
            # **Segunda Tela: PressB (e outras variáveis futuras)**
            oled.text(f"PressB: {pressB:.1f} hPa", 0, 0)
            # (Deixe espaço para mais sensores aqui)

        oled.show()
        screen = 1 - screen  # Alterna entre as telas

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        break

    time.sleep(5)  # Intervalo para alternar as telas
