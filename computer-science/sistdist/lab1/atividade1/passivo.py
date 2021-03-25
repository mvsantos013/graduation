import socket

HOST = ''   # Interface padrao de comunicacao da maquina
PORT = 5000 # Identifica o processo na maquina

# Criar o descritor socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # internet e tcp

# Vincular o endereço e porta
sock.bind((HOST, PORT))

# Colar em modo de espera
print(f'Listening at port {PORT}')
sock.listen(1) # Quantidade de conexoes pendentes

# Aceitar conexao
newSock, address = sock.accept()

print(f'connected to {address}')

while True:
    # Esperar por mensagem do lado ativo
    msg_bytes = newSock.recv(1024) # Qtd maxima de bytes

    msg = msg_bytes.decode('utf-8')

    if msg == 'exit()':
        break
    
    newSock.send(msg_bytes)

# Encerra conexao
print('Closing Connection')
newSock.close()
sock.close()