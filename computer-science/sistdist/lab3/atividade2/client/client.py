import socket
import json
from utils import encode_message, decode_message

HOST = ''  
PORT = 5003
SUCCESS = 200

sock = socket.socket() 
sock.connect((HOST, PORT))

msg_bytes = sock.recv(1024)
files = decode_message(msg_bytes).body
print('List of available files: \n - ' + '\n - '.join(files) + '\n')


while True:
    val = input('Choose a file or type exit to close:\n')

    if val == 'exit':
        break

    sock.send(encode_message(val))

    msg_bytes = sock.recv(1024)
    msg = decode_message(msg_bytes)

    if(msg.status != SUCCESS):
        print(msg.body + '\n')
        continue
    
    occurrences = msg.body
    
    print('\n--- Occurrences found ---')
    for word in occurrences:
        print(word + ': ' + str(occurrences[word]))
    print('-------------------------\n')


print('Closing Connection')
sock.close()