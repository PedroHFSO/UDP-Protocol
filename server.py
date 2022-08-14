import socket
import sys
import asyncio

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


async def receivePacket():
    # Listen for incoming datagram
    while(True):
        try:
            global address
            global current_ack
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            print('received packet')
            serial_num, msg = message.decode('utf-8').split('\\msg\\', 1) #divide o header da mensagem
            clientMsg = "Message do Client:{}".format(message)
            if int(serial_num) == current_ack: #recebeu o pacote esperado: ACK = serial number
                current_ack =  int(serial_num) + sys.getsizeof(str.encode(msg)) #Adiciona tamanho do pacote ao número serial do pacote pra retornar ACK
        except:
            pass
        await asyncio.sleep(0.1)

async def sendACK():
    while True:
        if address != -1:
            print('ACK Value:{}'.format(current_ack))
            UDPServerSocket.sendto(str.encode(str(current_ack)), address)
        await asyncio.sleep(0.1)

async def main():
    task = asyncio.create_task(sendACK()) #Envio de ACK
    task_2 = asyncio.create_task(receivePacket()) #Recebimento de pacotes
    await asyncio.wait([task, task_2])


asyncio.run(main())