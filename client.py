import socket
import sys

msgSequence = {
    'message': ['Primeira mensagem', 'Segundo pacote', 'ENvio 3'],
    'serial_number' : [0] #The serial number of the first packet is 0
}
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024

last_serial_number = 0
for msg in msgSequence['message']:
    byteSize = sys.getsizeof(str.encode(msg))
    msgSequence['serial_number'].append(last_serial_number + byteSize) #Sums the bytesize of each packet to the next serial number
    last_serial_number += byteSize #Update the last serial number


# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

for i in range(len(msgSequence['message'])):
    msg = msgSequence['message'][i]
    serial_number = msgSequence['serial_number'][i]
    #msgFromServer = UDPClientSocket.recvfrom(bufferSize) #tries to get ACK
    bytesToSend = str.encode(msg)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    print('Sent '+msg+' with serial number of '+str(serial_number))



