import socket
import threading

def receive_messages():
    while True:
        try:
            received_data = client_socket.recv(1024).decode()
            print(received_data)
        except ConnectionResetError:
            print("Server closed the connection unexpectedly")
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 12345

client_socket.connect((host, port))
username = input("Enter your username (max 16 characters): ")[:16]
client_socket.send(username.encode())
welcome_message = client_socket.recv(1024).decode()
print(welcome_message)
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

try:
    while True:
        response = input("")
        if response.lower() == 'exit':
            break
        message_to_send = f"{response}"
        client_socket.send(message_to_send.encode())

except KeyboardInterrupt:
    pass

finally:
    client_socket.close()
