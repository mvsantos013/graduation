import socket

HOST = 'localhost'
PORT = 5000

# Cria o descritor de socket
sock = socket.socket() # AF_INET, SOCK_STREAM

# Estabelece conexao
sock.connect((HOST, PORT))

while True:
    val = input('Envie uma mensagem ou digite exit() para sair:\n')

    sock.send(val.encode())

    if val == 'exit()':
        break

    # Recebe resposta do lado passivo
    msg_bytes = sock.recv(1024)
    
    msg = msg_bytes.decode('utf-8')
    print(f'Resposta do lado passivo: {msg}\n')

# Encerra conexao 
print('Closing Connection')
sock.close()

