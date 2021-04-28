from threading import RLock
lock = RLock()

users = {}
groups = {}

def fetch_users():
    return users

def login_user(user_id, sock, address):
    if(user_id in users):
        users[user_id]['sock'] = sock
        users[user_id]['address'] = address
        users[user_id]['status'] = 'online'
    else:
        users[user_id] = {
            'name': user_id,
            'sock': sock,
            'address': address,
            'status': 'online',
        }

def logout_user(user_id):
    users[user_id]['sock'] = None
    users[user_id]['address'] = None
    users[user_id]['status'] = 'offline'

def fetch_groups():
    return groups

def create_group(group_id, user_id):
    groups[group_id] = {
        'owner': user_id,
        'users': [user_id]
    }

def delete_group(group_id):
    del groups[group_id]

def add_user_to_group(group_id, user_id):
    groups[group_id]['users'].append(user_id)

def rmv_user_from_group(group_id, user_id):
    groups[group_id]['users'].remove(user_id)

