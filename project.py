import spidev
import time
import matrixbreakout
import os
import RPi.GPIO as GPIO

FRAME_TIME = 0.2
LEFT_BUTTON = 31
RIGHT_BUTTON = 11
QUIT_BUTTON = 36
spi = spidev.SpiDev()

should_close = False

def close_system(pin):
    global should_close
    should_close = True


def main():
    # Inicjalizacja pinów przycisków
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup([LEFT_BUTTON, RIGHT_BUTTON, QUIT_BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(QUIT_BUTTON, GPIO.RISING, callback=close_system)
    # Inicjalizacja wyświetlacza
    spi.open(0, 0)
    spi.max_speed_hz = 10**7 # Ustawienie poprawnej częstotliwości zegara
    spi.xfer([0x0B, 0x07]) # Uruchomienie wyświetlania wszystkich kolumn matrycy
    spi.xfer([0x0C, 0x01]) # Wyłączenie "shutdown mode"
    for i in range(8):
        spi.xfer([i+1, 0x00]) # Wyczyszczenie wyświetlacza dla pewności

    game = matrixbreakout.BreakoutGame()

    try:
        while not should_close:
            start_time = time.process_time_ns()
            # Obiekt game zajmuje się symulacją rozgrywki i generowaniem obrazu do wyświetlenia
            game.update((GPIO.input(LEFT_BUTTON) == GPIO.HIGH, GPIO.input(RIGHT_BUTTON) == GPIO.HIGH))
            board = game.board_matrix()
            for i, data in enumerate(board):
                spi.xfer([i+1, int(data)])
            # Przerwa między klatkami jest dostosowana zależnie od czasu przetwarzania klatki
            total_frame_time = time.process_time_ns() - start_time
            time.sleep(max(0, FRAME_TIME - total_frame_time/10**9))
    except:
        # Blok try except pozwoli programowi na wykonanie reszty kodu w przypadku próby zamknięcia przez inny proces.
        pass
    # Sprzątanie
    for i in range(8):
        spi.xfer([i + 1, 0x00])
    spi.xfer([0x0C, 0x00])
    spi.close()
    GPIO.cleanup()
    if should_close:
        os.system('sudo shutdown now') # Zamknij system jeżeli proces przerwano przyciskiem


if __name__ == '__main__':
    main()
