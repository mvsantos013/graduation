import sys
import socket
import select
import threading
import json
import application_protocol as ap
import database as db
import chat_manager as cm
from application_protocol import encode_message, decode_message
from logger import Logger, Colors as c

logger = Logger()
HOST, PORT = '', 5000

menu = '''Available commands:
\texit - Shutdown server
\tusers - Show active users
\tbroadcast: <message> - Broadcast a message to all users
\tkick user_id - Kicks a user from SistDist Chat
\thelp - Shows menu'''

class Server():
    def start(self):
        print('Starting server...')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen(0)
        self.sock.setblocking(False)
        
        self.inputs = [self.sock, sys.stdin]
        self.threads = []

        logger.info('Server is now online.')
        logger.info(f'Listening at port {PORT}')
        print(menu)

        while True:
            r, w, e = select.select(self.inputs, [], [])
            for ready in r:
                if ready == self.sock: # Handle sockets
                    self.socket_handler()
                elif ready == sys.stdin: # Handle command line
                    self.command_line_handler()

    def socket_handler(self):
        sock, address = self.sock.accept()
        # Start processing user requests in parallel.
        client = threading.Thread(target=self.process_requests, args=(sock, address))
        client.start()
        self.threads.append(client)
        
    def process_requests(self, sock, address):
        ''' Listen to messages from client. '''
        logger.info(f'New connection at {address}')

        # Get user_id from his first message (login).
        msg_bytes = sock.recv(1024)
        if msg_bytes.decode() == '':
            return

        user_id = decode_message(msg_bytes).body

        # Check if user is already online
        users = db.fetch_users()
        if(user_id in users and users[user_id]['status'] == 'online'):
            sock.send(encode_message(f'User {user_id} is already online in another device.', None, ap.STATUS_ERROR))
            return

        logger.info(f'User {user_id} is online.')

        # login user
        db.login_user(user_id, sock, address)

        # Tell others that user is online.
        for uid in users:
            if(uid != user_id and users[uid]['status'] == 'online'):
                users[uid]['sock'].send(encode_message(user_id, ap.MSG_TYPE_USER_LOGGED_IN))

        while True:
            msg_bytes = sock.recv(1024)
            if msg_bytes.decode() == '':
                break
                
            msg = decode_message(msg_bytes)

            users = db.fetch_users()
            groups = db.fetch_groups()

            logger.info(f'New message received from {user_id}. Message type:', msg.type)

            # Send users list
            if(msg.type == ap.MSG_TYPE_USERS):
                cm.send_users_list(user_id, msg.body, sock, users, groups)

            # Send message to an user
            elif(msg.type == ap.MSG_TYPE_MESSAGE):
                cm.send_message_to_user(user_id, msg.body, sock, users, groups)
            
            # Send message to a group
            elif(msg.type == ap.MSG_TYPE_MESSAGE_GROUP):
                cm.send_message_to_group(user_id, msg.body, sock, users, groups)

            # Send group list
            elif(msg.type == ap.MSG_TYPE_GROUPS):
                cm.send_group_list(user_id, msg.body, sock, users, groups)

            # Send group users list
            elif(msg.type == ap.MSG_TYPE_GROUP_USERS):
                cm.send_group_users_list(user_id, msg.body, sock, users, groups)

            # Create group
            elif(msg.type == ap.MSG_TYPE_ADD_GROUP):
                cm.create_group(user_id, msg.body, sock, users, groups)
            
            # Delete group
            elif(msg.type == ap.MSG_TYPE_RMV_GROUP):
                cm.delete_group(user_id, msg.body, sock, users, groups)
            
            # Add user to group
            elif(msg.type == ap.MSG_TYPE_ADD_GROUP_USER):
                cm.add_user_to_group(user_id, msg.body, sock, users, groups)

            # Remove user from group
            elif(msg.type == ap.MSG_TYPE_RMV_GROUP_USER):
                cm.rmv_user_from_group(user_id, msg.body, sock, users, groups)

            else:
                logger.info('Unkown message type received.')

        logger.info(f'Closed connection at {address}.')
        db.logout_user(user_id)

        # Tell others that user is offline.
        for uid in users:
            if(uid != user_id and users[uid]['status'] == 'online'):
                users[uid]['sock'].send(encode_message(user_id, ap.MSG_TYPE_USER_LOGGED_OFF))

    def command_line_handler(self):
        cmd = input()

        # These two lines is just to format user input in terminal
        print ("\033[A                             \033[A")
        print(c.white + '>' , cmd + c.reset)

        users = db.fetch_users()

        if cmd == 'exit':
            self.exit()
        
        elif cmd == 'help':
            print(menu)

        elif cmd == 'users':
            online_users = [ k for k, v in users.items() if v['status'] == 'online']
            if not online_users:
                print('There are no online users.')
                return
            print('Online users:\n', '\t' + '\n\t'.join(online_users))
        
        elif cmd.startswith('broadcast:'):
            msg = ':'.join(cmd.split(':')[1:]).strip()
            for user in users.values():
                if(user['status'] == 'online'):
                    user['sock'].send(encode_message(msg, ap.MSG_TYPE_SERVER_BROADCAST))
        
        elif(cmd.startswith('kick ')):
            user_id = cmd.split(' ')[-1]
            if(user_id in users and users[user_id]['sock']):
                users[user_id]['sock'].send(encode_message(None, ap.MSG_TYPE_BAN))
                users[user_id]['sock'].close()
                db.logout_user()
                print('User kicked successfuly.')
            else:
                print('User does not exist or is not online.')
        else:
            print('Invalid command. Type \'help\' to see available commands.')        

    def exit(self):
        logger.info('Shutting down server...')
        logger.info('Server is now offline.')
        sys.exit()

server = Server()
server.start()
