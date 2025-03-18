# Opis działania

## Uruchamianie serwera

Najpierw uruchamiamy `server.py`.  
Serwer można zatrzymać komendą `STOP` w konsoli.

## Uruchamianie klienta

Po uruchomieniu procesu klienta, podajemy w konsoli swój **nick**.  
Klient w wiadomości `innit` do serwera wysyła swój **nick** oraz swój **adres UDP**.

## Opcje klienta

Klient ma następujące opcje:

- **Zwykła wiadomość** – wysyłana do wszystkich klientów za pomocą **TCP**.
- **`LIST`** – wypisuje wszystkich, którzy kiedykolwiek połączyli się z serwerem.
- **`STOP`** – zatrzymuje proces klienta.
- **`U`** – wysyła ASCII art do wszystkich klientów za pomocą **UDP**.
- **`M`** – wysyła ASCII art multicastem do klientów za pomocą **UDP**  
  _(Serwer nie przetwarza tego multicastu)_.
