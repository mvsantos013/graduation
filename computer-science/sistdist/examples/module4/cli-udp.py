# Servidor de echo usando UDP: lado cliente
import socket

HOST = 'localhost' # endereco do servidor  
PORT = 7000    # porta de escuta do servidor     

# cria o socket de comunicacao
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Internet IPv4 + UDP

# endereco do servidor
dest = (HOST, PORT)

# envia uam sequencia de mensagens para o servidor e imprime a resposta
print ("Digite uma mensagem (para sair digite 'fim'):")
msg = input()
while msg != 'fim':
	# envia a mensagem para o servidor
	sock.sendto(msg.encode('utf-8'), dest)
	# aguarda a resposta do servidor e imprime
	msg, src = sock.recvfrom(1024)
	print(str(msg, encoding='utf-8'), src)
	msg = input()
# libera o socket
sock.close()