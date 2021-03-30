import os
import socket
import json

FILES_DIR = './files'
WORD_LIMIT = 10
HOST = ''  
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.bind((HOST, PORT))

print(f'Listening at port {PORT}')
sock.listen(1) 
newSock, address = sock.accept()
print(f'Connected to {address}')

# Send message with available files
files = [f for f in os.listdir(FILES_DIR) if f.endswith('.txt')]
msg = 'List of available files: \n - ' + '\n - '.join(files) + '\n'
newSock.send(msg.encode())

def process_file(filename):
    ''' Get 10 most frequent words in a file.
        Output example:
        { word1: count, word2: count, ... }
    '''
    result = {}
    with open(FILES_DIR + '/' + filename) as f:
        words = f.read().split()
        for word in words:
            word = word.strip()
            # Check if result can be edited.
            if((len(result) < WORD_LIMIT or word in result) and word):
                result[word] = result[word] + 1 if word in result else 1

    sorted_keys = sorted(result.items(), key=lambda item: item[1], reverse=True)
    sorted_result = { k: v for k, v in sorted_keys }
    return sorted_result


while True:
    msg_bytes = newSock.recv(1024)

    if msg_bytes.decode() == '':
        break

    msg = msg_bytes.decode('utf-8')
    
    if (msg not in files):
        newSock.send(b'Error: File not found.')
        continue
    
    occurrences = process_file(msg)
    
    msg = json.dumps(occurrences)

    newSock.send(msg.encode())

print('Closing Connection')
newSock.close()
sock.close()