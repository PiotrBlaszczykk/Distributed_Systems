import socket
import threading
from dataclasses import dataclass

clients = []
id_counter = 1
MAX_NO_CLIENTS = 5
BUFF_SIZE = 65536

SERVER_PORT = 8008
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', SERVER_PORT))

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('', SERVER_PORT))

print("uruchomiono serwer")

server_active = True

server_socket.listen(MAX_NO_CLIENTS)
print("serwer słucha")


#coś ala struct z C
@dataclass(frozen=False)
class Client:
    id: int
    socket: socket.socket
    nickname: str
    address: tuple
    udp_address: tuple
    is_active: bool

def handle_client(client):
    id = client.id
    client_socket = client.socket
    nickname = client.nickname
    address = client.address

    global server_active

    try:
        while server_active:

            data = client_socket.recv(BUFF_SIZE)
            print(f"wiadomość od {nickname}: " + data.decode("utf-8"))

            if not data:
                print("utracono połączenie z klientem")
                break

            decoded_data = data.decode("utf-8")

            if decoded_data == "STOP":
                print("klient postanowił się rozłączyć")
                break

            elif decoded_data == "LIST":

                response = "Lista klientów:\n"
                for c in clients:
                    response += f"ID: {c.id}, Nick: {c.nickname}, Status: {'Aktywny' if c.is_active else 'Nieaktywny'}\n"

                client_socket.send(response.encode("utf-8"))

            else:

                to_all_response = f"wiadomość od {nickname}: {decoded_data}"
                for c in clients:

                    if c.id != id and c.is_active:
                        c.socket.send(to_all_response.encode("utf-8"))

            # response = f"napisałeś do serwera: {data.decode('utf-8')}"
            # client_socket.send(response.encode("utf-8"))

    except Exception:
        print(f"coś poszło nie tak z klientem o id {id}")

    finally:
        client_socket.close()
        client.is_active = False
        print(f"zamknięto połączenie z klientem o id {id} i ustawiono jego status na niektywny")


def udp_listener():
    while server_active:
        try:

            data, client_addr = udp_server_socket.recvfrom(BUFF_SIZE)
            message = data.decode("utf-8")

            #szukamy od kogo mamy tą wiadomość, aby nie odsyłać z powrotem do niego co sam wysłał
            sender = None
            for c in clients:
                if c.udp_address == client_addr:
                    sender = c

            sender_nick = sender.nickname

            print(f"UDP od {sender_nick}:")
            print(message)

            for c in clients:
                if c.is_active and c is not sender:
                    udp_server_socket.sendto(data, c.udp_address)

        except Exception as e:
            print("coś poszło nie tak w UDP")
            udp_server_socket.close()
            break



#funkcja czytająca input do serwera
def read_funciton():

    while True:
        data = input()

        if data == "STOP":

            global server_active
            server_active = False
            info = "wyłączono serwer"

            for c in clients:

                if c.is_active:

                    c.socket.send(info.encode("utf-8"))
                    c.socket.close()

            server_socket.close()
            udp_server_socket.close()
            break

read_thread = threading.Thread(target=read_funciton)
read_thread.start()

udp_thread = threading.Thread(target=udp_listener)
udp_thread.start()

# główna pętla serwera
while server_active:

    try:
        if not server_active:
            break

        # wiadomość innit od klienta
        client_socket, client_address = server_socket.accept()
        print(f"serwer zaakceptował połączenie od {client_address}")
        data = client_socket.recv(BUFF_SIZE).decode("utf-8").strip()

        nickname, udp_port = data.split("_")
        client_udp_address = (client_address[0], int(udp_port))

        print(f"nick klienta: {nickname}")

        new_client = Client(
            id_counter,
            client_socket,
            nickname,            #w pierwszej wiadomości klient przesyła swój nick
            client_address,
            client_udp_address,  #w wiadomości innit klient przekazuje nam dodatkowo swój adres UDP
            True)

        thread = threading.Thread(target=handle_client, args=(new_client,))
        clients.append(new_client)
        response = f"witaj {nickname} twoje id to: {id_counter}"
        client_socket.send(response.encode("utf-8"))

        id_counter += 1
        thread.start()

    except OSError:
        print("zamknieto serwer")
        break

    except Exception as e:
        print("coś poszło nie tak")

#ostatni check żeby zamknąć socket
if server_socket:
    server_socket.close()
    udp_server_socket.close()
