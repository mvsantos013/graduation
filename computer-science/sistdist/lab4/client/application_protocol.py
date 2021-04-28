'''
    Application protocol.
    
    Messages between client and server has the following format:
    {
        status: string,
        type: string,
        body: any
    }

    There are constants below to help organizing the code and
    show all possible values.
    
    At the end of this file there are 
    functions to help enconding, decoding and acessing messages values.
'''

import json

STATUS_SUCCESS = 200
STATUS_ERROR = 500

MSG_TYPE_UNDEFINED = 'undefined'
MSG_TYPE_LOGIN = 'login'
MSG_TYPE_MESSAGE = 'message'
MSG_TYPE_MESSAGE_GROUP = 'message_group'
MSG_TYPE_SERVER_BROADCAST = 'server_broadcast'
MSG_TYPE_USER_LOGGED_IN = 'user_logged_in'
MSG_TYPE_USER_LOGGED_OFF = 'user_logged_off'
MSG_TYPE_USERS = 'users'
MSG_TYPE_GROUPS = 'groups'
MSG_TYPE_GROUP_USERS = 'group_users'
MSG_TYPE_ADD_GROUP = 'add_group'
MSG_TYPE_RMV_GROUP = 'rmv_group'
MSG_TYPE_ADD_GROUP_USER = 'add_group_user'
MSG_TYPE_RMV_GROUP_USER = 'rmv_group_user'
MSG_TYPE_BAN = 'ban'


# -------- Utility functions ----------

def encode_message(data = None, msg_type = None, status = 200):
    ''' Get message attributes and encode in binary. '''
    return json.dumps({ 'status': status, 'type': msg_type, 'body': data }).encode()

def decode_message(msg):
    ''' Decode message and return a Message object. '''
    return Message(json.loads(msg.decode('utf-8')))

class Message():
    ''' Message Class.
        It helps dealing with dict values, for example:
        Instead of accessing a value as message["body"] you
        can access the value as message.body
    '''
    def __init__(self, msg):
        self.status = msg['status']
        self.type = msg['type']
        self.body = msg['body']