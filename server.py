import socket
import sys
import asyncio

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server online e escutando")

# Listen for incoming datagrams
current_ack = 0
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    clientMsg = "Message do Client:{}".format(message)
    clientIP  = "Cliente com  IP Address:{}".format(address)
    print(clientMsg)
    #print(clientIP)
    current_ack += sys.getsizeof(message) #Adds size of packet to ack
    print('ACK Value:{}'.format(current_ack))

    # Sending a reply to client
    # spoiler de ACK
    UDPServerSocket.sendto(str.encode(str(current_ack)), address)
