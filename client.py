import socket
import sys
import asyncio  
import time
import random
import string
from datetime import date, datetime

#Definição de sequência de pacotes--------------------
# msgSequence = {
#     'message': ['Primeira mensagem', 'Segundo pacote', 'ENvio 3'],
#     'serial_number' : [0], #Primeiro número de série é 0
#     'confirmed': [False, False, False],
#     'timestamps': [0,0,0] #Momento de envio do pacote, para testar no timeout
# }
msgSequence = {
    'message': [],
    'serial_number': [0],
    'confirmed': [],
    'timestamps': []
}

num_pkts = 30
window_size = 10
window_first = 0

for i in range(num_pkts):
    letters = string.ascii_lowercase
    message = ''.join(random.choice(letters) for i in range(8))
    msgSequence['message'].append(message)
    msgSequence['confirmed'].append(False)
    msgSequence['timestamps'].append(0)

last_serial_number = 0

for msg in msgSequence['message']: #Define número de série de acordo com fluxo de bytes: Soma a quantidade de bytes de um pacote para o número de série do próximo
    byteSize = sys.getsizeof(str.encode(msg))
    msgSequence['serial_number'].append(last_serial_number + byteSize) #Somando o bytesize para o próximo paacote
    last_serial_number += byteSize 

#Other params--------------------
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Async functions
async def receiveACK():
    global window_first
    latestACK = '-1' #Nenhum ack recebido
    while(True):
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0] #Recebe ACK e converte pra int
        msgFromServer = int(msgFromServer)
        if msgFromServer != latestACK: #Caso seja um ACK novo: executa procedimento para confirmar (ou não) pacotes
            print('ack novo recebido')
            latestACK = msgFromServer
            for i in range(len(msgSequence['message'])):
                serial_num = msgSequence['serial_number'][i]
                if serial_num < latestACK and latestACK in msgSequence['serial_number']: #Se esse ACK for o número de série de algum pacote, confirma todos pra trás
                    msgSequence['confirmed'][i] = True
                    window_first += 1
            print(msgSequence['confirmed'])
        await asyncio.sleep(0.1) #Round robin

async def timeout(bytesToSend, serverAddressPort, i):
    print('antes de dormir')
    await asyncio.sleep(3)
    print('esperado')
    if not msgSequence['confirmed'][i]:
        print('pacote '+str(i)+' nao foi confirmado')
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)

async def sendPackets():
    for i in range(len(msgSequence['message'])):
        if i == window_first + window_size:
             i-=1
        else:
            msg = msgSequence['message'][i]
            serial_number = msgSequence['serial_number'][i]
            msgSequence['timestamps'][i] = datetime.timestamp(datetime.now())
            bytesToSend = str.encode(str(msgSequence['serial_number'][i])+'\\msg\\'+msg) #Codifica novo pacote com número de sequência + mensagem
            print('tried to send '+msg+' with serial number of '+str(serial_number))
            #if i != 1: #Não vou transmitir o pacote [1] só pra testar o timeout
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        await asyncio.sleep(0.1)

async def checkTimeouts():
    while(True):
        id = -1 #índice do primeiro pacote não confirmado
        for i in range(len(msgSequence['message'])):
            if not msgSequence['confirmed'][i]:
                id = i
                break
        if id == -1: #se não tiver nada não confirmado, n precisa fazer nada
            await asyncio.sleep(0.1)
        else:
            TIMEOUT_INTERVAL = 1
            now = datetime.timestamp(datetime.now())
            if(now - msgSequence['timestamps'][id] > TIMEOUT_INTERVAL and msgSequence['timestamps'][id] != 0):
                print('pacote '+str(i)+' estourou o tempo')

                for i in range(id, len(msgSequence['message'])):
                    if msgSequence['timestamps'][id] != 0: #retransmitir apenas pacotes que ja foram enviados antes
                        now = datetime.timestamp(datetime.now()) #Recapturar timestamp e retransmitir com o mais recente possível
                        msgSequence['timestamps'][i] = now
                        bytesToSend = str.encode(str(msgSequence['serial_number'][i])+'\\msg\\'+msgSequence['message'][i]) #Codifica novo pacote com número de sequência + mensagem
                        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                        print('retransmitindo '+msgSequence['message'][i])
                        #msgSequence['confirmed'][i] = True #TEM QUE RETRANSMITIR
            await asyncio.sleep(0.1) #Round robin

async def main(): #Chama funções para resolverem de forma concorrente
    task = asyncio.create_task(sendPackets()) #Envio de pacotes
    task_2 = asyncio.create_task(receiveACK()) #Recebimento de ACK
    task_3 = asyncio.create_task(checkTimeouts()) #Teste de estouro de timeouts
    await asyncio.wait([task, task_2, task_3])

asyncio.run(main())





