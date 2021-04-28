import sys
import os
import socket
import threading
import json
import application_protocol as ap
from application_protocol import encode_message, decode_message
from logger import Logger, Colors as c

logger = Logger('info')
HOST, PORT = '', 5000

menu = f'''Available commands:
\t{c.white}users{c.reset} - Show users.
\t{c.white}groups{c.reset} - Show groups.
\t{c.white}gusers group_id{c.reset} - Show users in a group.
\t{c.white}to user_id: <message>{c.reset} - Sends a message to an user.
\t{c.white}tog group_id: <message>{c.reset} - Sends a message to a group.
\t{c.white}add group_id{c.reset} - Create group.
\t{c.white}rmv group_id{c.reset} - Delete group.
\t{c.white}add group_id user_id{c.reset} - Add user to group.
\t{c.white}rmv group_id user_id{c.reset} - Remove user from group.
\t{c.white}help{c.reset} - Shows menu.
\t{c.white}exit{c.reset} - Leaves application.'''

class Client():
    def start(self):
        self.sock = socket.socket() 
        self.sock.connect((HOST, PORT))

        print(c.header + 'Welcome to SistDist Chat.', c.reset)

        self.login()

        print(menu)

        # Handle chat events (messages from server)
        self.socket_thread = threading.Thread(target=self.socket_handler, args=(), daemon = True)
        self.socket_thread.start()

        # Handle terminal commands
        while True:
            self.command_line_handler()

    def login(self):
        while True:
            self.user_id = input('Type your user ID to login (alphanumeric): ')
            if(self.user_id.isalnum()):
                break
            else:
                print(c.fail + 'User ID must have only letters or numbers.', c.reset)
        self.sock.send(encode_message(self.user_id, ap.MSG_TYPE_LOGIN))
        print('You are now connected to the chat.')

    def socket_handler(self):
        ''' Listen to messages from the server. '''
        while True:
            msg_bytes = self.sock.recv(1024)
            if msg_bytes.decode() == '':
                print(c.fail + 'Connection closed by the server.', c.reset)
                self.exit()

            msg = decode_message(msg_bytes)

            # Error sent by the server
            if(msg.status != ap.STATUS_SUCCESS):
                print(c.fail + msg.body, c.reset)
                continue
            
            # Message event
            if(msg.type == ap.MSG_TYPE_MESSAGE):
                print(f'{c.cyan}from {msg.body["from"]}{c.reset}: {msg.body["text"]}')

            # Group message event
            elif(msg.type == ap.MSG_TYPE_MESSAGE_GROUP):
                print(f'{c.cyan}from {msg.body["from"]} in group {msg.body["group"]}{c.reset}: {msg.body["text"]}')

            # Server broadcast event
            elif(msg.type == ap.MSG_TYPE_SERVER_BROADCAST):
                print(f'{c.purple}from Server: {msg.body}{c.reset}')
            
            # User login event
            elif(msg.type == ap.MSG_TYPE_USER_LOGGED_IN):
                print(f'{c.green}User {msg.body} is now online{c.reset}')
            
            # User logout event
            elif(msg.type == ap.MSG_TYPE_USER_LOGGED_OFF):
                print(f'{c.gray}User {msg.body} is now offline{c.reset}')
            
            # Users list command response
            elif(msg.type == ap.MSG_TYPE_USERS):
                if not msg.body.keys():
                    print('There are no online users.')
                    continue
                print('Users:')
                for user in msg.body.values():
                    color = c.green if user['status'] == 'online' else c.gray
                    print(f'\t{color}{user["name"]} ({user["status"]}){c.reset}')

            # Groups list command response
            elif(msg.type == ap.MSG_TYPE_GROUPS):
                if len(msg.body.keys()) == 0:
                    print('You aren\'t in any group yet. Type add <group_id> to create one.')
                    continue
                print('Groups you are participating:')
                for group_id in msg.body:
                    print('\t-', group_id, '(owner)' if msg.body[group_id] else '')                    

            # Group users list command response
            elif(msg.type == ap.MSG_TYPE_GROUP_USERS):
                print('Group users:')
                for uid in msg.body:
                    print('\t-', uid)
            
            # User added to group event
            elif(msg.type == ap.MSG_TYPE_ADD_GROUP_USER):
                print(c.yellow + f'User {msg.body["user_id"]} was added by {msg.body["adder_id"]} to group {msg.body["group_id"]}.', c.reset)

            # User removed from group event
            elif(msg.type == ap.MSG_TYPE_RMV_GROUP_USER):
                print(c.yellow + f'User {msg.body["user_id"]} was removed from group {msg.body["group_id"]}.', c.reset)

            # User ban event
            elif(msg.type == ap.MSG_TYPE_BAN):
                print(c.fail + 'You were kicked from the chat!', c.reset)
                self.exit()

            elif(msg.type == ap.MSG_TYPE_UNDEFINED):
                print(msg.body)
            
            else:
                print('Unkown message type received.')

    def command_line_handler(self):
        ''' Handle command line input and send messages. '''
        cmd = input()

        # These two lines is just to format user input in terminal
        print ("\033[A                             \033[A")
        print(c.white + '>' , cmd + c.reset)

        if cmd == 'exit':
            self.exit()
        
        elif cmd == 'help':
            print(menu)
        
        # List users
        elif cmd == 'users':
            self.sock.send(encode_message(None, ap.MSG_TYPE_USERS))
        
        # List groups
        elif cmd == 'groups':
            self.sock.send(encode_message(None, ap.MSG_TYPE_GROUPS))

        # List group users
        elif cmd.startswith('gusers '):
            group_id = cmd.split(' ')[-1]
            self.sock.send(encode_message(group_id, ap.MSG_TYPE_GROUP_USERS))

        # Send message to user
        elif cmd.startswith('to '):
            to_id, *text = cmd.split(':')
            to_id = to_id.split(' ')[-1]
            text = ':'.join(text).strip()
            self.sock.send(encode_message({'to': to_id, 'text': text}, ap.MSG_TYPE_MESSAGE))
        
        # Send message to group
        elif cmd.startswith('tog '):
            to_id, *text = cmd.split(':')
            to_id = to_id.split(' ')[-1]
            text = ':'.join(text).strip()
            self.sock.send(encode_message({'to': to_id, 'text': text}, ap.MSG_TYPE_MESSAGE_GROUP))

        elif cmd.startswith('add '):
            vals = cmd.split(' ')
            group_id = vals[1]

            # Create group
            if(len(vals) == 2):
                if(group_id.isalnum()):
                    self.sock.send(encode_message(group_id, ap.MSG_TYPE_ADD_GROUP))
                else:
                    print(c.fail + 'Group id must be alphanumeric.', c.reset)
            
            # Add user to group
            else:
                user_id = vals[2]
                self.sock.send(encode_message({'group_id': group_id, 'user_id': user_id}, ap.MSG_TYPE_ADD_GROUP_USER))

        elif cmd.startswith('rmv '):
            vals = cmd.split(' ')
            group_id = vals[1]
            
            # Delete group
            if(len(vals) == 2):
                self.sock.send(encode_message(group_id, ap.MSG_TYPE_RMV_GROUP))
            
            # Remove user from group
            else:
                user_id = vals[2]
                self.sock.send(encode_message({'group_id': group_id, 'user_id': user_id}, ap.MSG_TYPE_RMV_GROUP_USER))
        else:
            print('Invalid command. Type \'help\' to see available commands.') 
    
    def exit(self):
        print('Shutting down Client...')
        self.sock.close()
        print('Client closed successfuly.')
        os._exit(0)


client = Client()
client.start()