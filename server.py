import socket
import sys
import asyncio
import random


localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024
current_ack = 0
address = -1
msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)
# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.setblocking(0)
# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server online e escutando")
buffer = []
noLosses = True
bufferLimit = 1024 * 1000 * 600 #em segmentos

def receivePacket():
    # Listen for incoming datagram
    try:
        #if random.randint(0,100) >= 11: #1% de chance de descartar pacote            
        global address
        global buffer
        global current_ack
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        #print('received packet')
        serial_num, msg = message.decode('utf-8').split('\\msg\\', 1) #divide o header da mensagem
        if int(serial_num) == current_ack: #recebeu o pacote esperado: ACK = serial number
            if random.randint(0,10000) > 6 or noLosses: 
                current_ack =  int(serial_num) + sys.getsizeof(str.encode(msg)) #Adiciona tamanho do pacote ao número serial do pacote pra retornar ACK
                buffer.append(msg)
                #print('ACK Value:{}'.format(current_ack)
            else:
                print('pacote '+serial_num+' descartado')
    except:
        pass

def sendACK():
    if address != -1:
        UDPServerSocket.sendto(str.encode(str(current_ack)+'\\msg\\'+str(bufferLimit - len(buffer))), address)


sendACK()

while True:
    sendACK()
    receivePacket()
    #print(current_ack)