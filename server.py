import socket
import threading
import datetime

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)
print(f"Server listening on {host}:{port}")


usernames = {}
lock = threading.Lock()
log_file = open("chat_log.txt", "a")

def broadcast(message, sender_addr):
    with lock:
        for client_addr, (client_socket, _) in usernames.items():
            if client_addr != sender_addr:
                try:
                    client_socket.send(message.encode())
                except ConnectionResetError:
                    print(f"Connection with {client_addr} reset by the client")
                    remove_client(client_addr)

def remove_client(addr):
    with lock:
        del usernames[addr]


def log_message(sender_username, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {sender_username}: {message}\n"
    log_file.write(log_entry)
    log_file.flush()


def handle_client(client_socket, addr):
    try:
        username = client_socket.recv(16).decode()
        with lock:
            usernames[addr] = (client_socket, username)
        print(f"{username} has joined the chat.")

        # Welcome message to the client
        welcome_message = f"Welcome, {username}! You can start chatting."
        client_socket.send(welcome_message.encode())

        while True:
            received_data = client_socket.recv(1024).decode()
            if received_data.lower() == 'exit':
                break
            message_to_broadcast = f"[{username}]: {received_data}"
            broadcast(message_to_broadcast, addr)
            log_message(username, received_data)

    except ConnectionResetError:
        print(f"{username} has left the chat.")

    finally:
        remove_client(addr)
        client_socket.close()


try:
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Got connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

except KeyboardInterrupt:
    print("Server terminated by user")

finally:
    server_socket.close()
    log_file.close()
