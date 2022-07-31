import math
import random
import time

class Game():
    """ The main game object which contains current state like player positions,
        whether they have used any keys etc.
    """
    def __init__(self, width, height, p1_symbol='1', p2_symbol='2'):
        # dict with player info
        self.players = {
            '1': {
                'pos': (1, 1),
                'symbol' : p1_symbol,
                'key': None,
                'power-up': None,
                'has_used_key': False
            },
            '2': {
                'pos': (1, 1),
                'symbol' : p2_symbol,
                'key': None,
                'power-up': None,
                'has_used_key': False
            }
        }

        # board dimensions
        self.width = width
        self.height = height
        
        self.chest_x = 0
        self.chest_y = 0

        self.winner = False

        # message that may be displayed at the bottom 
        self.message = "@" * self.width
        self.messageTimer = 0

        self.board = [[" " for y in range(height)] 
                               for x in range(width)] 

        # x and y delta for each direction key
        self.direction_dict = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

    def set_player_position(self, player, pos):
        #set current player position 
        self.players[player]['pos'] = pos
    
    def get_player_position(self, player):
        #get current player position
        return self.players[player]['pos']

    def initBoard(self):
        """ Initiates the board by drawing its edges with blocking "#"s.
            Then adds the objects to it, which are:
            1. The chest
            2. The players
            3. Some random obstacles
            4. The keys
        """
        for i in range(self.height):
            self.board[0][i] = "#"
            self.board[self.width - 1][i] = "#"
        for i in range(self.width):
            self.board[i][0] = "#"
            self.board[i][self.height - 1] = "#"

        (self.chest_x, self.chest_y) = self.addChestToBoard()
        self.addPlayersToBoard()
        self.addRandomObstacles(30)
        self.addKeys()

    def printBoard(self):
        """ Prints the board on the server console for logging
            and debugging purposes.
        """
        for i in range(self.height):
            for j in range(self.width):
                print(self.board[j][i], end='')
            print('')
        
    def insertInBoard(self, pos, symbol):
        """ Insert symbol at position (x, y) on the board

        Args:
            pos: Tuple with (x,y) coords on board
            symbol: The character to be inserted
        """
        (x, y) = pos
        if(x >= 0 and x <= self.width and
           y >= 0 and y <= self.height):
            self.board[x][y] = symbol
    
    def addTuples(self, a, b):
        """ Add first arg to first arg and 
            second arg to second arg of two tuples
        """
        return (a[0] + b[0], a[1] + b[1])
    
    def isPlayerSym(self, c):
        """ Check if c is a player symbol

        Args:
            c : A character

        Returns:
            Boolean: true or false
        """
        for key in self.players:
            if c == self.players[key]['symbol']:
                return True
        return False
    
    def setMessage(self, message):
        """ Set a message(< 80 chars) to be displayed under the board in client

        Args:
            message : The string to be displayed
        """
        if len(message) < self.width:
            self.messageTimer = time.time()
            filler = " " * (self.width - len(message))
            self.message = message + filler
        else:
            print("That message is too big!")
    
    def resetMessage(self):
        """ Reset the message so nothing appears under board in client
        """
        self.message = "@" * self.width

    def validMove(self, player, pos):
        """ Checks to see if a player is trying to make a valid move,
            for example the player cannot move to a position marked with "#"

        Args:
            player : The player moving (1 or 2)
            pos : Tuple with (x,y) coords the player is moving to

        Returns:
            Boolean: True if move possible, false otherwise
        """        
        (x, y) = pos
        current_sym = self.board[x][y]

        on_key_has_key = (current_sym == 'K' and self.players[player]['key'])
        on_key_has_used_key = (current_sym == 'K' and self.players[player]['has_used_key'])
        on_gate_no_key = (current_sym == '=' and (not self.players[player]['key']))

        #we can't go to the next position if it is:
        #1, a '#' symbol (wall)
        #2, a 'K' (key) and the player already picked up a key
        #3, a 'K' (key) and the player has already used a key
        #4, another player
        #5, a gate and the player has no key
        if (current_sym == '#' 
            or on_key_has_key
            or on_key_has_used_key
            or self.isPlayerSym(current_sym) 
            or on_gate_no_key):
            return False

        return True

    def addChestToBoard(self):
        """ Add the chest container to the board.
            Taking the chest is the goal of the game

        Returns:
            tuple: Coords to where the chest was randomly inserted
        
        The chest container has an outer rim and an inner rim,
        and there are gates that require a key to open, marked with "="
        like the figure below:
        ###############
        #             #   
        #  #########  #
        #  #       #  #
        =  #   *   =  #
        #  #       #  #
        #  #########  #
        #             #
        ###############
        """
        chestWidth = 15
        chestHeight = 9
        innerChestWidth = 9
        innerChestHeight = 5

        (random_x, random_y) = self.getRandomChestPos(chestWidth, chestHeight)

        #add borders to chest container
        for x in range(chestWidth):
            #upper row
            self.board[random_x + x][random_y] = "#"
            #lower row
            self.board[random_x + x][random_y + chestHeight -1] = "#"
        for x in range(innerChestWidth):
            #inner upper row
            self.board[random_x + 3 + x][random_y + 2] = "#"
            #inner lower row
            self.board[random_x + 3 + x][random_y + innerChestHeight + 1] = "#"
        for y in range(chestHeight):
            #left column
            self.board[random_x][random_y + y] = "#"
            #right column
            self.board[random_x + chestWidth -1][random_y + y] = "#"
        for y in range(innerChestHeight):
            #inner left column
            self.board[random_x + 3][random_y + 2 + y] = "#"
            #inner right column
            self.board[random_x + 2 + innerChestWidth][random_y + 2 + y] = "#"
        
        outer_gate_y = random_y + 4
        inner_gate_x = random_x + chestWidth - 4 
        #remove eventual gate blockers
        self.board[random_x - 1][outer_gate_y] = " "
        self.board[inner_gate_x][random_y] = " "
        #add gates to chest container
        self.board[random_x][random_y + 4] = "="
        self.board[inner_gate_x][random_y + 4] = "="
        # self.board[random_x + 7][random_y + 4] = "*"
        return (random_x, random_y)

    def getRandomChestPos(self, width, height):
        """ Helper function to get a random starting position 
            for the chest container in a specific range 

        Args:
            width  : The total width of the chest
            height : The total height of the chest

        Returns:
            tuple: Coords to where the chest should be inserted
        """
        min_pos = (10, 10)
        max_pos = (self.width - width - 1,
                   self.height - height - 1)
        random_x = random.randint(min_pos[0], max_pos[0])
        random_y = random.randint(min_pos[1], max_pos[1])

        return (random_x, random_y)

    def addPlayersToBoard(self):
        """ Adds the player symbols to the board (1 and 2)
        """
        for key in self.players:
            self.insertInBoard(self.players[key]['pos'], self.players[key]['symbol'])
    
    def updateKeysAndMessage(self, player, sym):
        """ If a player picks up a key, or a player uses a key,
            we update their inventory and send a message to client

        Args:
            player : The player moving (1 or 2)
            sym: The character to be inserted
        """        
        if sym == 'K':
            self.players[player]['key'] = True
            self.setMessage(f"Player {player} picked up a new key!")
        elif sym == '=':
            self.players[player]['key'] = False
            self.players[player]['has_used_key'] = True
            self.setMessage(f"Player {player} used their key to open a gate!")
        elif sym == '*':
            self.winner = True

    def makeMove(self, direction, player):
        """ Update player position based on direction input and
            add new position to the board. Also decide if message
            has been displayed long enough.

        Args:
            direction : up/down/left/right
            player : The player moving (1 or 2)
        """
        player = str(player)
        increment = self.direction_dict[direction]
        current_pos = self.get_player_position(player)
    
        # clear previous position
        self.insertInBoard(current_pos, ' ')

        new_pos = self.addTuples(increment, current_pos)

        if self.validMove(player, new_pos):
            (x, y) = new_pos
            sym_on_new_pos = self.board[x][y]
            self.updateKeysAndMessage(player, sym_on_new_pos)
            self.set_player_position(player, new_pos)
        
        # log player inventory and position etc on every move
        print(self.players)
        if time.time() - self.messageTimer > 5:
            self.resetMessage()
        # update the board according to new player positions etc. 
        self.addPlayersToBoard()

    def addRandomObstacles(self, amount):
        """ Add obstacles '#' at random positions on the board

        Args:
            amount : The amount of obstacles to add
        """
        for i in range(amount):
            xpos = random.randint(2, self.width - 1)
            ypos = random.randint(2, self.height - 1)
            has_obstacle = self.board[xpos][ypos] == "#"
            within_chest = ((xpos > self.chest_x and xpos < self.chest_x + 15) and 
                            (ypos > self.chest_y and ypos < self.chest_y + 9))

            while (has_obstacle or within_chest):
                #random anew
                xpos = random.randint(2, self.width - 1)
                ypos = random.randint(2, self.height - 1)
            self.insertInBoard((xpos, ypos), "#")

    def addKeys(self):
        """ Add two keys to the board,
            they are used to open gates in the chest to win.
        """
        for i in range(2):
            xpos = random.randint(2, self.width - 1)
            ypos = random.randint(2, self.height - 1)
            # position already has key or
            while(self.board[xpos][ypos] == "K" or (
            # position is within the chest
            (xpos > self.chest_x and xpos < self.chest_x + 15) and
            (ypos > self.chest_y and ypos < self.chest_y + 9))):
                # random anew
                xpos = random.randint(2, self.width - 1)
                ypos = random.randint(2, self.height - 1)
            self.insertInBoard((xpos, ypos), "K")

    def boardToString(self):
        """ Convert the 2D array that is the board to a string
            which can then be sent to client.

        Returns:
            string: The string which represents the current game state
        """
        if self.winner:
            gameString = "W" * 2400
        else:
            gameString = ""
            for i in range(0, self.height):
                for j in range(0, self.width):
                    gameString += self.board[j][i]
        return gameString + self.message