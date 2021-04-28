import rpyc
from threading import Thread
from logger import Logger, bcolors as c

log = Logger()
PORT = 10000

server = rpyc.connect('localhost', PORT)
log.cyan('Connected to chat server.')

menu = {
    '1': 'Exibir usuários',
    '2': 'Enviar mensagem',
    '4': 'Exibir meus grupos',
    '5': 'Criar um grupo',
    '6': 'Adicionar um usuário a um grupo a qual pertenço',
    '7': 'Remover um usuário de um grupo a qual pertenço',
    '8': 'Excluir grupo',
    '9': 'Exibir menu novamente',
    'exit': 'Sair'
}

def login():
    ''' Defines a user_id. '''
    print('Bem-vindo ao SistDist Chat.')
    user_id, valid = None, False
    while (not valid):
        user_id = input('Digite seu ID de usuário (somente letras e números): ')
        if(user_id.isalnum()):
            valid = True
    try:
        server.root.login(user_id)
    except Exception as e:
        print(e)

def show_menu():
    ''' Shows menu options.'''
    print('Opções disponíveis:')
    for op in menu:
        print(f'\t{op}: {menu[op]}')
    print()

def subscribe_to_events():
    ''' Passes the event callback to the server '''
    server.root.subscribe_to_events(on_event)

def on_event(event):
    ''' Called by the server everytime a event for the user occurs. '''
    if(event['type'] == 'user_status_update'):
        payload = event['payload']
        user_id = payload['user_id']
        status = payload['status']
        print(f'{c.OKGREEN}User {user_id} is now {status}.{c.ENDC}')

    return

def run():
    while True:
        op = input('Escolha uma opção: ')
        if op == 'exit':
            server.close()
            break
        
        elif op == '1':
            users = server.root.get_users()
            if(len(users) == 0):
                print('Não há outros usuários ainda.')
                continue
            print('Usuários:')
            for user_id in users:
                user = users[user_id]
                print(f'\t{user["name"]} ({user["status"]})')

        else:
            show_menu()
            
login()
show_menu()
subscribe_to_events()
run()

