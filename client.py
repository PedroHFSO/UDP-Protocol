import socket
import sys
import asyncio 
import time
import random
import string
from datetime import date, datetime

#---------------DEFINIÇÃO DE PACOTES---------------
msgSequence = {
    'message': [],
    'serial_number': [0],
    'confirmed': [],
    'timestamps': []
}

num_pkts = 30
window_size = 1
window_first = 0
current_pkt = 0
latestACK = '-1' #Nenhum ack recebido
rwnd = 1000
non_confirmed = 0 #Índice do primeiro pacote não confirmado
n = 0 #Número de pacotes confirmados
ssthresh = -1

def defaultPackets():
    for i in range(num_pkts):
        letters = string.ascii_lowercase
        message = ''.join(random.choice(letters) for i in range(100))
        msgSequence['message'].append(message)
        msgSequence['confirmed'].append(False)
        msgSequence['timestamps'].append(0)

    last_serial_number = 0

    for msg in msgSequence['message']: #Define número de série de acordo com fluxo de bytes: Soma a quantidade de bytes de um pacote para o número de série do próximo
        byteSize = sys.getsizeof(str.encode(msg))
        msgSequence['serial_number'].append(last_serial_number + byteSize) #Somando o bytesize para o próximo paacote
        last_serial_number += byteSize 

def filePackets():
#---------------PACOTES ARQUIVO 10MB---------------
    last_serial_number = 0
    f=open('testfile',"rb") 
    data = f.read(1000)
    while (data):
        byteSize = sys.getsizeof(data)
        msgSequence['serial_number'].append(last_serial_number + byteSize)
        last_serial_number+=byteSize
        msgSequence['message'].append(data.decode('utf-8'))
        msgSequence['confirmed'].append(False)
        msgSequence['timestamps'].append(0)
        data = f.read(1000)


#-------------------SOCKET STUFF--------------------
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def checkTimeouts():
    global window_size
    print('check')
    id = -1 #índice do primeiro pacote não confirmado
    for i in range(current_pkt):
        if not msgSequence['confirmed'][i]:
            id = i
            break
    if id != -1: #apenas checar timeout se tiver algo confirmado
        TIMEOUT_INTERVAL = 10 #10 segundos
        now = datetime.timestamp(datetime.now())
        if(now - msgSequence['timestamps'][id] > TIMEOUT_INTERVAL and msgSequence['timestamps'][id] != 0):
            print('pacote '+str(i)+' estourou o tempo')

            for i in range(id, len(msgSequence['message'])):
                if msgSequence['timestamps'][id] != 0: #retransmitir apenas pacotes que ja foram enviados antes
                    now = datetime.timestamp(datetime.now()) #Recapturar timestamp e retransmitir com o mais recente possível
                    msgSequence['timestamps'][i] = now
                    bytesToSend = str.encode(str(msgSequence['serial_number'][i])+'\\msg\\'+msgSequence['message'][i]) #Codifica novo pacote com número de sequência + mensagem
                    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                    print('retransmitindo '+str(msgSequence['serial_number'][i]))
                    window_size /= 2
                    #msgSequence['confirmed'][i] = True #TEM QUE RETRANSMITIR

def receiveACK():
    print('receive')
    global window_first
    global rwnd
    global non_confirmed
    global window_size
    global latestACK
    global n
    new_acks = False
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0]
    ack, rwnd = msgFromServer.decode('utf-8').split('\\msg\\', 1) #divide o header da mensagem
    msgFromServer = int(ack)
    while msgFromServer != latestACK: #Busca maior ACK da janela
        print('ack novo recebido: '+str(msgFromServer))
        latestACK = msgFromServer
        new_acks = True 
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0]
        ack, rwnd = msgFromServer.decode('utf-8').split('\\msg\\', 1) #divide o header da mensagem
        msgFromServer = int(ack)
    rwnd = int(rwnd)
    if new_acks:
        for i in range(non_confirmed, len(msgSequence['message'])):
            serial_num = msgSequence['serial_number'][i]
                
            if serial_num <= latestACK: #Se esse ACK for o número de série de algum pacote, confirma todos pra trás
                msgSequence['confirmed'][i] = True
                n+=1
                if serial_num == latestACK:
                    non_confirmed = i + 1
                    break        
        if ssthresh > 0 and window_size > ssthresh: #congestion avoidance
            window_size += 1     
        else:
            window_size *= 2 #slow start: inicia dobrando  
        if window_size > len(msgSequence['confirmed']):
            window_size = len(msgSequence['confirmed'])
        if window_size > rwnd:
            window_size = rwnd

def sendPackets(): #envia todos os pacotes da janela de envios
    global current_pkt 
    print('send')
    for i in range(current_pkt, current_pkt + window_size):
        if i < len(msgSequence['confirmed']): #há pacote para enviar / buffer de pacotes não acabou
            msg = msgSequence['message'][i]
            serial_number = msgSequence['serial_number'][i]
            msgSequence['timestamps'][i] = datetime.timestamp(datetime.now())
            bytesToSend = str.encode(str(serial_number)+'\\msg\\'+msg) #Codifica novo pacote com número de sequência + mensagem
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            print('tried to send '+msg+' with serial number of '+str(serial_number)+' and size of'+str(sys.getsizeof(str.encode(msg))))
            current_pkt += 1

j = 0
filePackets()
while True:
    j+=1
    sendPackets()
    checkTimeouts()
    receiveACK()
    if(False not in msgSequence['confirmed']): #todos os pacotes enviados com sucesso
        break