import socket
import json
import database
from utils import encode_message, decode_message
from config import HOST, PORT, WORD_LIMIT, SUCCESS, ERROR, MSG_FILE_NOT_FOUND

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.bind((HOST, PORT))

print(f'Listening at port {PORT}')
sock.listen(1) 
newSock, address = sock.accept()
print(f'Connected to {address}')

# Send message with available files
files = database.fetch_files()
newSock.send(encode_message(files))

def process_file(filename):
    ''' Get 10 most frequent words in a file.
        Output example:
        { word1: count, word2: count, ... }
    '''
    result = {}
    words = database.read_file(filename).split()
    for word in words:
        word = word.strip()
        # Check if result can be edited.
        if((len(result) < WORD_LIMIT or word in result) and word):
            result[word] = result[word] + 1 if word in result else 1

    sorted_keys = sorted(result.items(), key=lambda item: item[1], reverse=True)
    sorted_result = { k: v for k, v in sorted_keys }
    return sorted_result


while True:
    while True:
        msg_bytes = newSock.recv(1024)
    
        if msg_bytes.decode() == '':
            break
            
        msg = decode_message(msg_bytes).body
        
        if (msg not in files):
            newSock.send(encode_message(MSG_FILE_NOT_FOUND, ERROR))
            continue
        
        occurrences = process_file(msg)
        newSock.send(encode_message(occurrences))
    
    print(f'Listening at port {PORT}')
    sock.listen(1) 
    newSock, address = sock.accept()
    print(f'Connected to {address}')
    newSock.send(encode_message(files))


print('Closing Connection')
newSock.close()
sock.close()