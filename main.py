from machine import I2C, Pin
import time
from mpu6050_temp import MPU6050
from AHT20 import AHT20
from bmp280 import BMP280

# Configurações do hardware
SDA_PIN = 18
SCL_PIN = 19
I2C_FREQ = 100000

print("=== Inicializando Sensores I2C ===")
print(f"Config: SDA=GPIO{SDA_PIN}, SCL=GPIO{SCL_PIN}, Freq={I2C_FREQ} Hz")

# Inicializa o barramento I2C
i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)

# Verifica se há dispositivos no barramento
devices = i2c.scan()
if not devices:
    print("ERRO: Nenhum dispositivo I2C encontrado!")
else:
    print(f"Dispositivos encontrados: {[hex(d) for d in devices]}")

# Instancia os sensores
mpu_sensor = MPU6050(i2c)
aht_sensor = AHT20(i2c)
bmp_sensor = BMP280(i2c)

# Loop de leitura
print("\nLendo dados dos sensores... (pressione CTRL+C para parar)")
while True:
    try:
        print("-" * 20)
        
        # MPU6050
        temp_mpu = mpu_sensor.get_temperature()
        if temp_mpu is not None:
            print(f"MPU6050: Temperatura = {temp_mpu:.2f} °C")
        
        # AHT20
        temp_aht, hum_aht = aht_sensor.get_data()
        if temp_aht is not None and hum_aht is not None:
            print(f"AHT20: Temp = {temp_aht:.2f} °C, Umidade = {hum_aht:.2f} %")
            
        # BMP280
        temp_bmp, press_bmp = bmp_sensor.get_data()
        if temp_bmp is not None and press_bmp is not None:
            print(f"BMP280: Temp = {temp_bmp:.2f} °C, Pressão = {press_bmp:.2f} hPa")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        
    time.sleep(2) # Intervalo entre as leituras