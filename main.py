from machine import Pin, I2C, ADC
import time
from ssd1306 import SSD1306
from mpu6050_temp import MPU6050
from AHT20 import AHT20
from bmp280 import BMP280
from bmp180 import BMP180
import onewire
import ds18x20
from ntc import NTC
from dht11 import DHT11  # Importa sua classe personalizada

# === CONFIGURAÇÕES DOS SENSORES ===
# Barramento I2C 1 (Sensores Originais)
SDA1_PIN = 18
SCL1_PIN = 19
i2c1 = I2C(1, sda=Pin(SDA1_PIN), scl=Pin(SCL1_PIN), freq=100000)

# Barramento I2C 0 (BMP180 e Display OLED)
SDA0_PIN = 16
SCL0_PIN = 17
i2c0 = I2C(0, sda=Pin(SDA0_PIN), scl=Pin(SCL0_PIN), freq=100000)

# DS18x20 (OneWire no pino 2)
ds_pin = Pin(2, Pin.IN)
ds = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds.scan()
if not roms:
    print("ERRO: Nenhum sensor DS18x20 encontrado no pino 2!")
else:
    print(f"Sensor DS18x20 encontrado: {roms}")

# NTC (ADC no pino 28)
ntc_sensor = NTC(28)

# DHT11 (Pino Digital 12) - Usando sua implementação personalizada
try:
    dht_sensor = DHT11(Pin(12))
    print("Sensor DHT11 inicializado com sucesso no pino 12.")
except Exception as e:
    print(f"ERRO: Falha ao inicializar DHT11: {e}")
    dht_sensor = None

# === INICIALIZAÇÃO DOS DISPOSITIVOS I2C ===
print("\n=== Inicializando Sensores nos Barramentos I2C ===")

# Barramento 1
print(f"\n--- Barramento I2C 1 (SDA={SDA1_PIN}, SCL={SCL1_PIN}) ---")
devices1 = i2c1.scan()
if not devices1:
    print("ERRO: Nenhum dispositivo encontrado no barramento 1!")
else:
    print(f"Dispositivos encontrados: {[hex(d) for d in devices1]}")
    mpu_sensor = MPU6050(i2c1)
    aht_sensor = AHT20(i2c1)
    bmp280_sensor = BMP280(i2c1)

# Barramento 0
print(f"\n--- Barramento I2C 0 (SDA={SDA0_PIN}, SCL={SCL0_PIN}) ---")
devices0 = i2c0.scan()
if not devices0:
    print("ERRO: Nenhum dispositivo encontrado no barramento 0!")
else:
    print(f"Dispositivos encontrados: {[hex(d) for d in devices0]}")
    bmp180_sensor = BMP180(i2c0)
    oled = SSD1306(128, 64, i2c0)

# === LOOP PRINCIPAL ===
print("\nLendo dados dos sensores... (pressione CTRL+C para parar)")
screen = 0

while True:
    try:
        print("-" * 50)
        
        # Leitura dos sensores I2C e OneWire
        tempA = mpu_sensor.get_temperature()
        tempB, umidA = aht_sensor.get_data()
        tempC, pressA = bmp280_sensor.get_data()
        tempD, pressB = bmp180_sensor.get_data()
        
        tempE = None
        if roms:
            ds.convert_temp()
            time.sleep_ms(750)
            tempE = ds.read_temp(roms[0])
            
        tempF = ntc_sensor.get_temperature()
        
        # Leitura do DHT11 com múltiplas tentativas
        tempG, umidB = None, None
        if dht_sensor:
            success = False
            for attempt in range(3):  # Tenta até 3 vezes
                try:
                    if dht_sensor.measure():
                        tempG = dht_sensor.temperature()
                        umidB = dht_sensor.humidity()
                        success = True
                        break
                except Exception as e:
                    print(f"Tentativa {attempt+1} de leitura do DHT11 falhou: {e}")
                    time.sleep_ms(100)  # Pequeno atraso entre tentativas
            
            if not success:
                print("ERRO: Falha total na leitura do DHT11 após 3 tentativas")

        # Exibição no console
        print(f"TempA (MPU6050) = {tempA:.2f} C" if tempA is not None else "TempA: Falha")
        print(f"TempB (AHT20) = {tempB:.2f} C, UmidA = {umidA:.2f} %" if tempB is not None else "TempB/UmidA: Falha")
        print(f"TempC (BMP280) = {tempC:.2f} C, PressA = {pressA:.2f} hPa" if tempC is not None else "TempC/PressA: Falha")
        print(f"TempD (BMP180) = {tempD:.2f} C, PressB = {pressB:.2f} hPa" if tempD is not None else "TempD/PressB: Falha")
        print(f"TempE (DS18B20) = {tempE:.2f} C" if tempE is not None else "TempE: Falha")
        print(f"TempF (NTC) = {tempF:.2f} C" if tempF is not None else "TempF: Falha")
        print(f"TempG (DHT11) = {tempG:.2f} C, UmidB = {umidB:.2f} %" if tempG is not None else "TempG/UmidB: Falha")

        # Exibição no display OLED
        oled.fill(0)
        
        if screen == 0:
            # Primeira Tela: Temperaturas
            oled.text(f"TempA: {tempA:.1f}C" if tempA is not None else "TempA:--", 0, 0)
            oled.text(f"TempB: {tempB:.1f}C" if tempB is not None else "TempB:--", 0, 10)
            oled.text(f"TempC: {tempC:.1f}C" if tempC is not None else "TempC:--", 0, 20)
            oled.text(f"TempD: {tempD:.1f}C" if tempD is not None else "TempD:--", 0, 30)
            oled.text(f"TempE: {tempE:.1f}C" if tempE is not None else "TempE:--", 0, 40)
            oled.text(f"TempF: {tempF:.1f}C", 0, 50)
        else:
            # Segunda Tela: DHT11 e outros dados
            oled.text(f"Temp G: {tempG:.2f}C" if tempG is not None else "Temp G: --.-C", 0, 0)
            oled.text(f"Umid B: {umidB:.2f}%" if umidB is not None else "Umid B: --.-%", 0, 10)
            oled.text(f"PressA: {pressA:.1f}" if pressA is not None else "PressA:----", 0, 20)
            oled.text(f"PressB: {pressB:.1f}" if pressB is not None else "PressB:----", 0, 30)
            oled.text(f"UmidA: {umidA:.1f}%" if umidA is not None else "UmidA: --.-%", 0, 40)
            
        oled.show()
        screen = 1 - screen
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado no loop principal: {e}")
        break
        
    time.sleep(5)