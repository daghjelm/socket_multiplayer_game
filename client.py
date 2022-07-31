import socket
import curses

from _thread import *
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65000  # The port used by the server
#board dimensions
WIDTH = 80
HEIGHT = 30
#max size of board + message string
TOTAL_SIZE = WIDTH * HEIGHT + WIDTH

def stringToBoard(gameString, screen):
    """ Convert the string received from the server to 
        curses graphic and display on the terminal

    Args:
        gameString : The 2400 chars that make up the game board.
        screen : The ncurses window
    """
    for i in range(31):
        rowStr = gameString[0:80]
        gameString = gameString[80:]
        screen.addstr(i, 0, rowStr)

def listenerDrawer(screen, sock):
    """ Listen for server messages and draw a new screen
        when we receive a new string from the server

    Args:
        screen : The ncurses window
        sock : Socket that has settings etc when passed to this function
    """
    while True:
        try:
            received = ""
            #receive message from server
            while(len(received) < TOTAL_SIZE):
                received += sock.recv(TOTAL_SIZE - len(received)).decode("utf-8")

            screen.clear()
            if(received[0] == "W"):
                winScreen(screen)
            else:
                #board graphics
                gameString = received[0:(WIDTH * HEIGHT)]
                #info message
                message = received[(WIDTH * HEIGHT):]
                #display new board and message
                stringToBoard(gameString, screen)
                addServerMessageToBoard(message, screen)
                screen.refresh()
        except:
            error_message = "Error while receiving data from server"
            filler = " " * (WIDTH - len(error_message))
            error_message = error_message + filler
            addServerMessageToBoard(error_message, screen)
            continue

def winScreen(screen):
    """ When game is over, this function display the winner message
        on the ncurses screen.

    Args:
        screen : The ncurses window
    """
    for i in range(HEIGHT):
        screen.addstr(i, 35, "WINNER!", curses.A_BLINK)
        time.sleep(0.5)
        screen.refresh()

def addServerMessageToBoard(message, screen):
    """ Add the info message from server to the terminal with curses

    Args:
        message : At most 80 chars in a string from server
        screen : The ncurses window
    """
    if(message[0] == "@"):
        pass
    else:
        message = message.strip()
        screen.addstr(HEIGHT, 0, message)

def main(screen):
    """ Contains the main loop for the client, which accepts user
        input as keyboard presses on the "wasd" keys.

    Args:
        screen : The ncurses window

    Raises:
        e:  Raises any error another level so it can be caught
            in the ncurses wrapper.

    """
    screen.clear()
    if(curses.LINES < HEIGHT or curses.COLS < WIDTH):
        screen.addstr(0,0, "Your terminal window is too small to display the board")
        screen.addstr(2,0, "Please resize it and restart this program")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        #start a thread that listens and draws
        start_new_thread(listenerDrawer, (screen, sock))
        try:
            #send correct direction to server base on use input
            while True:
                userInput = screen.getkey() # this does a refresh
                if userInput == "w":
                    userInput = "up"
                elif userInput == "a":
                    userInput = "left"
                elif userInput == "s":
                    userInput = "down"
                elif userInput == "d":
                    userInput = "right"
                else:   #nothing happens if you didn't press "wasd"
                    continue
                byte_message = bytes(userInput, 'utf-8')
                sock.sendall(byte_message)
        except Exception as e:
            raise e

if __name__ == "__main__":
    curses.wrapper(main)
