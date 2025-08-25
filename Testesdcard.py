# datalogger_rtc.py - Registra data e hora no SD Card com botão de ejeção segura
import os
import machine
import time
from sdcard import SDCard

# --- Configuração do Hardware ---

# LED onboard para feedback visual
led = machine.Pin("LED", machine.Pin.OUT)

# Botão de Ejeção Segura no GP3
# Conexão: Um pino do botão -> GP3, outro pino -> 3V3 (Pino 36)
eject_button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Configuração do Hardware SPI(1) - Pinos Físicos 14, 15, 16, 17
spi = machine.SPI(1,
                  baudrate=1000000,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))
cs = machine.Pin(13, machine.Pin.OUT)

# --- Inicialização ---

print("Inicializando o sistema de registro...")

# Monta o cartão SD
try:
    sd = SDCard(spi, cs)
    os.mount(sd, '/sd')
    print("✓ Cartão SD montado com sucesso.")
except Exception as e:
    print(f"✗ Falha crítica ao montar o cartão SD: {e}")
    print("O programa será interrompido.")
    raise

# Inicializa o Relógio de Tempo Real (RTC)
rtc = machine.RTC()

# IMPORTANTE: Na primeira vez que rodar, descomente a linha abaixo
# e ajuste para a data e hora atuais para acertar o relógio.
# Formato: (ano, mês, dia, dia_da_semana, hora, minuto, segundo, microssegundo)
# Exemplo para 25 de Agosto de 2025, 18:13:00 (Segunda-feira = 0)
# rtc.datetime((2025, 8, 25, 0, 18, 13, 0, 0))

# Define o nome do arquivo de log
log_file_path = '/sd/timelog3.csv'

# Cria o arquivo com cabeçalho se ele não existir
try:
    with open(log_file_path, 'r') as f:
        pass # Arquivo já existe, não faz nada
    print(f"✓ Usando arquivo de log existente: {log_file_path}")
except OSError:
    # O arquivo não existe, então o criamos com um cabeçalho
    with open(log_file_path, 'w') as f:
        f.write("Timestamp\n")
    print(f"✓ Novo arquivo de log criado: {log_file_path}")

print("\n--- REGISTRO INICIADO ---")
print("Pressione o botão no GP3 para desmontar o cartão com segurança.")

# --- Loop Principal ---
while True:
    # Verifica se o botão de ejeção foi pressionado
    if eject_button.value() == 1:
        print("\nBotão de ejeção pressionado. Finalizando...")
        break

    # Pega a data e hora atual do RTC
    current_time = rtc.datetime()
    
    # Formata a data e hora em uma string amigável
    timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[0], current_time[1], current_time[2],
        current_time[4], current_time[5], current_time[6]
    )

    # Abre o arquivo no modo 'append' (adicionar) e salva a nova linha
    try:
        with open(log_file_path, 'a') as f:
            f.write(f"{timestamp_str}\n")
        
        # Pisca o LED rapidamente para indicar que um registro foi salvo
        led.on()
        time.sleep_ms(50)
        led.off()
        
        print(f"Registro salvo: {timestamp_str}")

    except Exception as e:
        print(f"✗ Erro ao salvar no arquivo: {e}")

    # Espera 5 segundos para o próximo registro
    time.sleep(5)

# --- Finalização e Ejeção Segura ---
print("\nDesmontando o sistema de arquivos do cartão SD...")
try:
    os.umount('/sd')
    print("✓ Cartão SD desmontado com segurança!")
    
    # Pisca o LED 5 vezes para sinalizar que é seguro remover o cartão
    for _ in range(5):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)
        
except Exception as e:
    print(f"✗ Erro ao desmontar o cartão SD: {e}")

print("Programa finalizado. É seguro remover o cartão.")
