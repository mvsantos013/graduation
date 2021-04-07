import sys
import socket
import select
import multiprocessing
import json
import database
import utils
from utils import encode_message, decode_message

HOST = ''  
PORT = 5003
ERROR = 500
MSG_FILE_NOT_FOUND = 'Error: File not found.'

class Server():
    def run(self):
        ''' Starts server.
            Fetch files and open socket to new connections.
        '''
        print('Starting server...')
        print('Fetching available files...')
        self.filenames = database.fetch_files()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.bind((HOST, PORT))
        self.sock.listen(5)
        self.sock.setblocking(False)
        
        self.inputs = [self.sock, sys.stdin]
        self.connections = {}
        self.clients = []

        print('Server is now online.')
        print(f'Listening at port {PORT}')

        while True:
            r, w, e = select.select(self.inputs, [], [])
            for ready in r:
                if ready == self.sock:
                    sock, address = self.sock.accept()
                    self.connections[sock] = address
                    print(f'New connection at {address}')
                    client = multiprocessing.Process(target=self.process_request, args=(sock, address))
                    client.start()
                    self.clients.append(client)

                elif ready == sys.stdin: 
                    cmd = input()
                    if cmd == 'server exit':
                        if self.hasConnections():
                            print(f'Server has active {len(self.connections)} connections.')
                            print('Waiting for active clients to close connection...')
                        for c in self.clients:
                            c.join()
                        self.exit()
                        return
                    elif cmd == 'server exit --force': 
                        for c in self.clients:
                            c.terminate()
                        self.exit()
                        return
                    elif cmd == 'server connections':
                        print('Connections:')
                        print(str(self.connections.values()))
                    elif cmd == 'server help':
                        print('Available commands:')
                        print('- server exit [--force]\n- server connections\n- server help')
                    else:
                        print('Invalid command. Type \'server help\' to see available commands.')

    def process_request(self, sock, address):
        sock.send(encode_message(self.filenames))
        ''' Process client request '''
        while True:
            msg_bytes = sock.recv(1024)
        
            if msg_bytes.decode() == '':
                break
                
            msg = decode_message(msg_bytes).body
            
            if (msg not in self.filenames):
                sock.send(encode_message(MSG_FILE_NOT_FOUND, ERROR))
                continue
            
            text = database.read_file(msg)
            occurrences = utils.count_occurrences(text)
            sock.send(encode_message(occurrences))
    
    def exit(self):
        print('Shutting down server...')
        self.sock.close()
        print('Server is now offline.')
    
    def hasConnections(self):
        return bool(self.connections)

server = Server()
server.run()
