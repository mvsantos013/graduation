import application_protocol as ap
from application_protocol import encode_message, decode_message
import database as db

def send_users_list(caller_id, body, sock, users, groups):
    users_list = { k: {'name': v['name'], 'status': v['status']} for k, v in users.items() if k != caller_id }
    sock.send(encode_message(users_list, ap.MSG_TYPE_USERS))
    return

def send_message_to_user(caller_id, body, sock, users, groups):
    to_id = body['to']
    if(to_id in users and users[to_id]['status'] == 'online'):
        mbody = { 'from': caller_id, 'text': body['text']}
        users[to_id]['sock'].send(encode_message(mbody, ap.MSG_TYPE_MESSAGE))
    else:
        sock.send(encode_message(f'User {to_id} is not online.', None, ap.STATUS_ERROR))

def send_message_to_group(caller_id, body, sock, users, groups):
    to_id = body['to']
    if to_id not in groups:
        sock.send(encode_message(f'Group {to_id} does not exist.', None, ap.STATUS_ERROR))
        return
    if caller_id not in groups[to_id]['users']:
        sock.send(encode_message(f'You are not in group {to_id}.', None, ap.STATUS_ERROR))
        return
    mbody = { 'from': caller_id, 'group': to_id, 'text': body['text'] }
    for uid in groups[to_id]['users']:
        if(uid != caller_id and users[uid]['status'] == 'online'):
            users[uid]['sock'].send(encode_message(mbody, ap.MSG_TYPE_MESSAGE_GROUP))

def send_group_list(caller_id, body, sock, users, groups):
    # Returns a dict like {group_id: True, group_id: False} where the boolean tells if user is owner.
    groups_list = { k: (True if v['owner'] == caller_id else False) for k, v in groups.items() if caller_id in v['users'] }
    sock.send(encode_message(groups_list, ap.MSG_TYPE_GROUPS))

def send_group_users_list(caller_id, body, sock, users, groups):
    group_id = body
    if group_id not in groups:
        sock.send(encode_message(f'Group {group_id} does not exist.', None, ap.STATUS_ERROR))
        return
    if caller_id not in groups[group_id]['users']:
        sock.send(encode_message(f'You are not in group {group_id}.', None, ap.STATUS_ERROR))
        return
    users_list = [uid for uid in groups[group_id]['users']]
    sock.send(encode_message(users_list, ap.MSG_TYPE_GROUP_USERS))

def create_group(caller_id, body, sock, users, groups):
    group_id = body
    if group_id in groups:
        sock.send(encode_message('This group already exists.', None, ap.STATUS_ERROR))
        return
    db.create_group(group_id, caller_id)

def delete_group(caller_id, body, sock, users, groups):
    group_id = body
    if group_id not in groups:
        sock.send(encode_message(f'Group {group_id} does not exist.', None, ap.STATUS_ERROR))
        return
    if groups[group_id]['owner'] != caller_id:
        sock.send(encode_message(f'Only the owner can dissolve a group.', None, ap.STATUS_ERROR))
        return
    db.delete_group(group_id)

def add_user_to_group(caller_id, body, sock, users, groups):
    group_id = body['group_id']
    user_id_added = body['user_id']
    if(group_id not in groups):
        sock.send(encode_message(f'Group {group_id} does not exist.', None, ap.STATUS_ERROR))
        return
    if(caller_id not in users):
        sock.send(encode_message(f'User {user_id_added} does not exist.', None, ap.STATUS_ERROR))
        return
    if(user_id_added not in groups[group_id]['users']):
        db.add_user_to_group(group_id, user_id_added)
        # Tell group members
        for uid in groups[group_id]['users']:
            if(users[uid]['status'] == 'online'):
                mbody = { 'group_id': group_id, 'adder_id': caller_id, 'user_id': user_id_added }
                users[uid]['sock'].send(encode_message(mbody, ap.MSG_TYPE_ADD_GROUP_USER))

def rmv_user_from_group(caller_id, body, sock, users, groups):
    group_id = body['group_id']
    user_id_rmvd = body['user_id']
    if(group_id not in groups):
        sock.send(encode_message(f'Group {group_id} does not exist.', None, ap.STATUS_ERROR))
        return
    if(caller_id not in users):
        sock.send(encode_message(f'User {user_id_rmvd} does not exist.', None, ap.STATUS_ERROR))
        return
    if groups[group_id]['owner'] != caller_id:
        sock.send(encode_message(f'Only the owner can remove a group member.', None, ap.STATUS_ERROR))
        return
    # Tell group members
    for uid in groups[group_id]['users']:
        if(users[uid]['status'] == 'online'):
            mbody = { 'group_id': group_id, 'user_id': user_id_rmvd }
            users[uid]['sock'].send(encode_message(mbody, ap.MSG_TYPE_RMV_GROUP_USER))
    db.rmv_user_from_group(group_id, user_id_rmvd)