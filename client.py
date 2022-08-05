import socket
import sys
import asyncio  
import time

#Message definition--------------------
msgSequence = {
    'message': ['Primeira mensagem', 'Segundo pacote', 'ENvio 3'],
    'serial_number' : [0], #The serial number of the first packet is 0
    'confirmed': [False, False, False]
}
pkt_sent_recently = -1 #no packet was sent yet
last_serial_number = 0

for msg in msgSequence['message']:
    byteSize = sys.getsizeof(str.encode(msg))
    msgSequence['serial_number'].append(last_serial_number + byteSize) #Sums the bytesize of each packet to the next serial number
    last_serial_number += byteSize #Update the last serial number

#Other params--------------------
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Async functions
async def receiveACK():
    latestACK = '-1' #flag for no ack received
    while(True):
        await asyncio.sleep(0.5)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0] #Receive message of packet
        msgFromServer = int(msgFromServer)
        if msgFromServer != latestACK:
            latestACK = msgFromServer
            for i in range(len(msgSequence['message'])):
                serial_num = msgSequence['serial_number'][i]
                if serial_num < latestACK and latestACK in msgSequence['serial_number']:
                    msgSequence['confirmed'][i] = True
            print(msgSequence['confirmed'])

async def timeout(bytesToSend, serverAddressPort, i):
    print('antes de dormir')
    await asyncio.sleep(3)
    print('esperado')
    if not msgSequence['confirmed'][i]:
        print('pacote '+str(i)+' nao foi confirmado')
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)

async def sendPackets():
    for i in range(len(msgSequence['message'])):
        msg = msgSequence['message'][i]
        serial_number = msgSequence['serial_number'][i]
        #await asyncio.create_task(receiveACK())
        #msgFromServer = UDPClientSocket.recvfrom(bufferSize) #tries to get ACK
        bytesToSend = str.encode(msg)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        pkt_sent_recently = i #signals which packet to check for timeout
        #task = asyncio.create_task(timeout(bytesToSend, serverAddressPort, i))
        #await task
        #await timeout(bytesToSend, serverAddressPort, i)
        print('Sent '+msg+' with serial number of '+str(serial_number))

async def checkTimeouts():
    while(True):
        if pkt_sent_recently:
            pkt_sent_recently = False
            await asyncio.sleep(4)

async def main():
    task = asyncio.create_task(sendPackets())
    task_2 = asyncio.create_task(receiveACK())
    task_3 = asyncio.create_task(checkTimeouts())
    await asyncio.wait([task, task_2])

asyncio.run(main())





