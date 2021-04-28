import sys
import socket
import threading
import json
import application_protocol as ap
from application_protocol import encode_message, decode_message
from logger import Logger, bcolors as c

logger = Logger('info')
HOST, PORT = '', 5000

menu = '''Available options:
\tusers - Show users
\tgroups - Show groups
\tto user_id: <message> - Sends a message to an user.
\tto group_id: <message> - Sends a message to a group.
\tadd group_id - Create group
\trmv group_id - Delete group
\tadd group_id user_id - Add user to group
\trmv group_id user_id - Remove user from group
\thelp - Shows menu
\texit - Leaves application'''


class Client():
    def start(self):
        self.sock = socket.socket() 
        self.sock.connect((HOST, PORT))

        print('Welcome to SistDist Chat.')

        self.login()

        print(menu)

        # Handle chat events (messages from server)
        self.socket_thread = threading.Thread(target=self.socket_handler, args=(), daemon = True)
        self.socket_thread.start()

        # Handle terminal commands
        while True:
            self.command_line_handler()

    def login(self):
        self.user_id = input('Type your user ID to login: ')
        self.sock.send(encode_message(self.user_id, ap.MSG_TYPE_LOGIN))

    def socket_handler(self):
        ''' Listen to messages from the server. '''
        while True:
            msg_bytes = self.sock.recv(1024)
            if msg_bytes.decode() == '':
                print('Connection closed by the server.')
                self.exit()

            msg = decode_message(msg_bytes)

            if(msg.status != ap.STATUS_SUCCESS):
                print(msg.body)
                continue
            
            if(msg.type == ap.MSG_TYPE_MESSAGE):
                print(f'from {msg.body["from"]}: {msg.body["text"]}')

            elif(msg.type == ap.MSG_TYPE_SERVER_BROADCAST):
                print(f'from Server: {msg.body}')
            
            elif(msg.type == ap.MSG_TYPE_USER_LOGGED_IN):
                print(f'User {msg.body} is now online')
            
            elif(msg.type == ap.MSG_TYPE_USER_LOGGED_OFF):
                print(f'User {msg.body} is now offline')
            
            elif(msg.type == ap.MSG_TYPE_USERS):
                if not msg.body.keys():
                    print('There are no online users.')
                    continue
                print('Users:')
                for user in msg.body.values():
                    print(f'\t{user["name"]} ({user["status"]})')

            elif(msg.type == ap.MSG_TYPE_BAN):
                print('You were banned from the chat!')
                self.exit()

            elif(msg.type == ap.MSG_TYPE_UNDEFINED):
                print(msg.body)
            
            else:
                print('Unkown message type received.')

    def command_line_handler(self):
        ''' Handle command line input and send messages. '''
        cmd = input()
        if cmd == 'exit':
            print('Closing Connection')
            self.exit()
        
        elif cmd == 'help':
            print(menu)
        
        elif cmd == '1':
            self.sock.send(encode_message(None, ap.MSG_TYPE_USERS))
        
        elif cmd.startswith('to '):
            to_id, *text = cmd.split(':')
            to_id = to_id.split(' ')[-1]
            text = ':'.join(text).strip()
            self.sock.send(encode_message({'to': to_id, 'text': text}, ap.MSG_TYPE_MESSAGE))
        
        else:
            print('Invalid command. Type \'help\' to see available options.') 
    
    def exit(self):
        print('Shutting down Client...')
        self.sock.close()
        print('Client closed successfuly.')
        sys.exit()


client = Client()
client.start()