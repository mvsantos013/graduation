import rpyc
from rpyc.utils.server import ThreadedServer
from logger import Logger

log = Logger()
PORT = 10000
users = {}

class Server(rpyc.Service):
    def on_connect(self, connection):
        self.connection = connection
        log.cyan('New connection.')
    

    def on_disconnect(self, connection):
        for user_id in users:
            if(users[user_id]['connection'] == self.connection):
                users[user_id]['connection'] = None
                users[user_id]['status'] = 'offline'
                break
        self.dispatch_user_status_update(user_id)
        log.cyan('Connection closed.')


    def exposed_login(self, user_id):
        ''' Add user to user list. '''

        if(user_id in users and users[user_id]['status'] == 'online'):
            raise Exception('User is already connected.')

        users[user_id] = {
            'connection': self.connection,
            'on_event_callback': None,
            'name': user_id,
            'status': 'online',
            'groups': []
        }
        self.dispatch_user_status_update(user_id)
        return
    

    def exposed_subscribe_to_events(self, on_event_callback):
        ''' Subscribe user to events. '''
        for user_id in users:
            if(users[user_id]['connection'] == self.connection):
                users[user_id]['on_event_callback'] = rpyc.async_(on_event_callback)
        return


    def exposed_get_users(self):
        ''' Retrieve all users. '''
        r = {}
        for user_id in users:
            user = users[user_id]
            if(user['connection'] == self.connection): # Ignore current user
                continue
            r[user_id] = {'name': user['name'], 'status': user['status']}
        return r


    def dispatch_user_status_update(self, event_user_id):
        ''' Dispatch event everytime a user login/logoff. '''
        for user_id in users:
            user = users[user_id]
            if(user_id == event_user_id or user['status'] == 'offline'): # Ignore target user and offline users
                continue
            
            user['on_event_callback']({
                'type': 'user_status_update',
                'payload': {
                    'user_id': event_user_id,
                    'status': users[event_user_id]['status'],
                }
            })
        return


server = ThreadedServer(Server, port=PORT)
log.cyan(f'Server is online. Listening at port {PORT}.')
server.start()
print(1111)