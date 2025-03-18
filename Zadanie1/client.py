import socket
import threading
import os
import struct

ASCII_ART = """
                          .:=*#@@@@@@@%#+=:.                                  
                      .*@@@@@@@@@@@@@@@@@@@@@@#:                              
                  .-%@@@@@@@@@@@@@@@@@@@@@@@@@%%@@*:                          
                :#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#.                       
              .@@@@@@@@@@@@@@@@@@@@@@@@%##********#@=#@*                      
            .#@@@@@@@@@@@@@@@@@@%#*++++=++++++*@@%##%@*:                       
           -@@@@@@@@@+++++++@@%***#%@*++++++*@@%######@@*                      
          %@%%+#@@@@@@++++%%*%@@@@@%#%@+++++%-:: ..     #+                     
        .@@@*#@+@@@@@@@*+*#:: ..      -@%%#@%-:::@%.    :@#**=:.               
       .%%*@#+++#%@@@@@++@-::.%@:      @+==+%-:--:.     *#-----=%@=           
       %@*****+++====++++%+::.        .@+++##+===--*@*:*%=+++==----%%:        
      *@***+==========++++%-::       .%*+++====+++===-@#++++======---%*       
     -@***+===========+++++@=::     -@++++++==+++++===*#++=========---+@.     
    .%#***+=+===========++++=#@%#%@%+=+=++++++++++++++@*+========++==--=#.    
    =@***+++++==========+++++=+++++=+==++*@#**++++**%@*==+===++=======--#+    
    @#***+=+++++========++%@#++++++++++++++*%@@@@@@#++++++=++++++++==+=--%.   
   +@***+=+++++=========+++==#@%#++++++++++++++++++++++%@+=+++=+++++===--*#   
  .@#***++++++=========++=+++==++*%@@%*++++++++++++*%@@%+++++++++=+++===--@.  
  +@****=+++++==========================+******+++=====+@%+++++===++++++=-%+  
 .@#***+=+++++===========================================-*@==+===++++++=-=%  
 :@****+++++++=====================================+++++=*@+=======+++++=--@: 
 =@****+++++++======================================+++*@*==+=======++====-#- 
 *%***+++++++=====================================++++#%+===========+++===-*+ 
.#%***++=+++=====================================++++@#++++==========+++==-+* 
.%#***+==++=====================================++++@*++++++++++++====++==-+*.
.@#***+++++=====================++++============+++===*@%+++++++++====+===-=*.
:@#***+++++================++++++++++==============+====-#%++++++++====+++-=#.
:@#***+++++================++++++++++++==============+++==*%=++++++====+++==#.
:@#***+++++================+++++@++++++++++++++++++++++++=-@+=+++++==+++++==#:
:@#***+++++===============+++++@@+++++++++++++++++++++++++=@*=+++++===++++==#:
:@#***++++++==============+++++#@++++++++++++++++++++++++++@===+=++===+++++=#:
%@#***++++++===============+++++@%*++++++++++%@*+++++++++*@*==========+++++=#:
=@#***+++++++===============+++++#@#+++++++%@**@@#**++*%@#+============+++++#:
=*@#**++++++++=================+++*+#@@@@@**+++++**###+++=============++++++%:
==+@%*+++++++++===================++++++++++===+========================++++#*
====#@*++++++++=======================================================+++++**.
=====:@#+++++++++====================================================+++++*@. 
@+==.  :%#+++++++++================================================++++++#%.  
=%#:     :@#++++++++++=========================================++=++++++#*    
:=*@:      :%#++++++++=======================================++==++++++%+    =
"""


serverIP = "127.0.0.1"
SERVER_PORT = 8008
BUFFER_SIZE = 65536

print("uruchomiono klienta \n proszę podać swój nick")

my_nickname = input()

client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp.connect((serverIP, SERVER_PORT))

client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp.bind(("", 0))
udp_port = client_udp.getsockname()[1]

#multicast

MULTICAST_GROUP = "224.0.0.1"
MULTICAST_PORT = 5005

multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

local_ip = socket.gethostbyname(socket.gethostname())

mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP), socket.inet_aton(local_ip))
multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 1))
multicast_socket.bind(("", MULTICAST_PORT))

multicast_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
multicast_send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 1))
multicast_send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, struct.pack("b", 0))

multicast_send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))

# mało eleganckie rozwiązanie, aby nie otrzymać od samego siebie multicastu,
# ale multicast loop działa na IP, a tutaj lokalnie wszyscy klienci mają to samo ip,
I_sent_multicast = False


#wiadomość innit

innit_msg = my_nickname + "_" + str(udp_port)
client_tcp.send(innit_msg.encode("utf-8"))

response = client_tcp.recv(BUFFER_SIZE).decode("utf-8")

print("wiadomość innit od serwera: " + response)

# Wyciągamy nasze ID z odpowiedzi
my_id = response.split()[-1]
#print(f"ID test: {my_id}")
active = True

def recv_tcp():

    global active
    while active:
        try:
            response = client_tcp.recv(BUFFER_SIZE)

            if not response:
                print("utracono połączenie z serwerem")
                client_tcp.close()
                client_udp.close()
                os._exit(0)

            print("serwer: " + response.decode("utf-8"))

        except Exception:
            print("coś poszło nie tak")
            active = False
            client_tcp.close()
            client_udp.close()
            multicast_socket.close()
            multicast_send_socket.close()
            os._exit(0)


def recv_udp():

    global active
    while active:
        try:
            response = client_udp.recv(BUFFER_SIZE)

            print("serwer: \n" + response.decode("utf-8"))

        except Exception:
            print("coś poszło nie tak")
            active = False
            client_tcp.close()
            client_udp.close()
            multicast_socket.close()
            multicast_send_socket.close()
            os._exit(0)


def recv_multicast():

    global I_sent_multicast
    global active
    while active:
        try:
            response = multicast_socket.recv(BUFFER_SIZE)

            if I_sent_multicast:
                I_sent_multicast = False
            else:
                print("multicast: \n" + response.decode("utf-8"))


        except Exception:
            print("coś poszło nie tak")
            active = False
            client_tcp.close()
            client_udp.close()
            os._exit(0)


def send_function():

    global active

    while active:
        try:

            message = input()

            if message == "U":
                client_udp.sendto(ASCII_ART.encode("utf-8"), (serverIP, SERVER_PORT))
                print("Wysłano ASCII Art do wszystkich")

            elif message == "M":
                global I_sent_multicast
                I_sent_multicast = True
                multicast_send_socket.sendto(ASCII_ART.encode("utf-8"), (MULTICAST_GROUP, MULTICAST_PORT))
                print("Wysłano ASCII Art przez multicast")

            elif message == "STOP":
                client_tcp.send(message.encode("utf-8"))
                active = False
                client_tcp.close()
                client_udp.close()
                multicast_socket.close()
                multicast_send_socket.close()
                os._exit(0)

            else:
                client_tcp.send(message.encode("utf-8"))


        except Exception as e:
            print("coś poszło nie tak: ", e)
            active = False
            client_tcp.close()
            client_udp.close()
            multicast_socket.close()
            multicast_send_socket.close()
            os._exit(0)

recv_thread = threading.Thread(target=recv_tcp)
send_thread = threading.Thread(target=send_function)
udp_thread = threading.Thread(target=recv_udp)
multicast_thread = threading.Thread(target=recv_multicast)

recv_thread.start()
send_thread.start()
udp_thread.start()
multicast_thread.start()

recv_thread.join()
send_thread.join()
udp_thread.join()
multicast_thread.join()

