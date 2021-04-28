#Servidor de echo usando UDP: lado do servidor
import socket
import select
import sys

HOST = ''  # podera receber mensagens de qualquer interface de rede disponivel
PORT = 7000   # porta para receber as mensagens

# cria o socket de comunicacao UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Internet IPv4 + UDP

# vindula o endereco para receber mensagens
sock.bind((HOST, PORT))

# espera e responde mensagens e finaliza quando for digitado 'fim'
while True:
	print("Aguardando mensagem ou finalizacao (digitar 'fim'):")
	# espera por novas mensagens ou pela entrada padrão
	r, w, e = select.select([sock, sys.stdin],[],[])
	for pronto in r:
		if pronto == sock: # nova mensagem de um cliente remoto
			msg, cliente = pronto.recvfrom(1024)
			print (cliente, str(msg, encoding='utf-8'))
			pronto.sendto(msg, cliente) #ecoa a mensagem do cliente
		else:
			cmd = input() # le a entrada padrao e finaliza 
			if cmd == 'fim': 
				sock.close()
				sys.exit() 