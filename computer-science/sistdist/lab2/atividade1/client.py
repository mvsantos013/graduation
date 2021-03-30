import socket
import json

HOST = 'localhost'
PORT = 5000

sock = socket.socket() 
sock.connect((HOST, PORT))

msg_bytes = sock.recv(1024)
msg = msg_bytes.decode('utf-8')
print(msg)

while True:
    val = input('Choose a file or type exit() to close:\n')

    if val == 'exit()':
        break

    sock.send(val.encode())

    msg_bytes = sock.recv(1024)
    
    msg = msg_bytes.decode('utf-8')

    if(msg == 'Error: File not found.'):
        print(msg + '\n')
        continue
    
    occurrences = json.loads(msg)
    
    print('Occurrences found:')
    for word in occurrences:
        print(word + ': ' + str(occurrences[word]))
    print()

print('Closing Connection')
sock.close()