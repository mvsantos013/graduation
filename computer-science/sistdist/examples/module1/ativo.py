import socket

HOST = 'localhost'
PORT = 5000

# Cria o descritor de socket

sock = socket.socket() # AF_INET, SOCK_STREAM

# Estabelece conexao
sock.connect((HOST, PORT))

sock.send(b'Ola, sou o lado ativo')

# Receber resposta do lado passivo
msg = sock.recv(1024)
print(msg.decode('utf-8'))

# Encerra conexao 
sock.close()

