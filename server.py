import socket
import sys
import time

import game
import threading
from _thread import *

HOST = "127.0.0.1"
PORT = 65000
turn_lock = threading.Lock()
#list of the client connection objects
connections = []

def appendConnection(conn):
    """ Append connection to correct index if the connections list

    Args:
        conn : the connection to client (fd) returned upon socket.accept()

    Returns:
        The "player" number which is just connections index + 1
        or -1 if we cannot add any more connections
    """
    # to begin with we just append the connections
    if(len(connections) < 2):
        connections.append(conn)
        return len(connections)
    # if we get here, it means that a client has disconnected
    # and is trying to connect again
    # so we need to add the connection object to the correct index
    else:
        for i, c in enumerate(connections):
            if c == None: # client has disconnected here
                print("Replacing connection: " + str(i))
                connections[i] = conn
                return i + 1
        # no connections were "None" so we already have two players connected
        return -1
        
def listen(sock, g):
    """ Function for listening to socket and then handling new client connections

    Args:
        sock : socket that has settings etc when passed to this function
        g : the game object
    """
    sock.listen(5)
    while True:
        # accept  new connection
        conn, addr = sock.accept()
        # append connection object and get player nr
        player = appendConnection(conn)
        if player == -1:
            print("Can't handle more than two clients")
            continue
        conn.settimeout(300) # 5min
        print(f"Connected by {addr}")
        # start a new thread that handles communication with the 
        # newly added client
        start_new_thread(clientCommunicator, (conn, g, player))

def clientCommunicator(conn, g, player):
    """ The main function for communication with client.
        Should always be run from a separate thread.
        Receives messages, updates game state and responds with new state.

    Args:
        conn : the connection to client (fd) returned upon socket.accept()
        g : the game object
        player : the player who is making the move (1 or 2)

    Raises:
        error: when a disconnection happens, we update the connections array
    """
    try:
        byte_message = bytes(g.boardToString(), 'utf-8')
        conn.sendall(byte_message)
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:    # connection is closed
                raise error("Client disconnected")
            print("Received: " + str(data))

            if not data in ["up", "down", "left", "right"]:
                g.message = "Invalid move sent to server"
            else:
                # wait for lock to be released before making a 
                # move to prevent race conditions in the game object
                turn_lock.acquire()
                g.makeMove(data, player)
                turn_lock.release()

            byte_message = bytes(g.boardToString(), 'utf-8')
            g.printBoard()
            # send updated board to all clients
            for c in connections: 
                try:
                    c.sendall(byte_message)
                except Exception as e:
                    print(e)

    except Exception as e:
        connections[player - 1] = None
        print(e)
        conn.close()

def main():
    # init a new game object
    g = game.Game(80, 30)
    g.initBoard()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # enable using an already existing socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))

            # listen for new connections
            listen(s, g)

        except KeyboardInterrupt:
            s.close()
            sys.exit()
        except Exception as e:
            print(e)
            print(e.__class__)
            s.close()

if __name__ == "__main__":
    main()


