'''
(Modified by Gang, Woohyun for Animal Shogi.)

Author: Eric P. Nichols
Date: Feb 8, 2008.
Board class.
Board data:
  1=white, -1=black, 0=empty
  first dim is column , 2nd is row:
     pieces[1][7] is the square in column 2,
     at the opposite end of the board in row 8.
Squares are stored and manipulated as (x,y) tuples.
x is the column, y is the row. (equivalent to files and ranks in chess - Gang, Woohyun)
'''
import numpy as np

class Board():

    # Movements of each pieces.
    # Chicks' movements are asymmetrical, so the black chick is handled specifically.
    __directions = [[(0, -1)],  # 0: Black chick
        [(0, 1)],  # 1: White chick
        [(1,1),(1,-1),(-1,-1),(-1,1)],  # 2: Elephant
        [(1,0),(0,-1),(-1,0),(0,1)],  # 3: Giraffe
        [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]]  # 4: Lion

    def __init__(self):
        "Set up initial board configuration."
        
        # Create the empty board array.
        self.pieces = [None] * 3
        for i in range(3):
            self.pieces[i] = [0] * 4

        # Set up the pieces at init.
        self.pieces[0][0] = 2
        self.pieces[1][0] = 4
        self.pieces[2][0] = 3
        self.pieces[1][1] = 1
        self.pieces[1][2] = -1
        self.pieces[0][3] = -3
        self.pieces[1][3] = -4
        self.pieces[2][3] = -2

         # Create the list for Mochikomas
        self.BlackMochi = []
        self.WhiteMochi = []
        
        self.draw_counter = 0

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]
    
    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(4):
            for x in range(3):
                count += self[x][y]
        return count * color
    
    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black
        """
        moves = set()  # stores the legal moves.
        mochilist = self.WhiteMochi if color == 1 else self.BlackMochi # given color's Mochiuma list

        # Get all the squares with pieces of the given color.
        for y in range(4):
            for x in range(3):
                if np.sign(self[x][y]) == color:
                    newmoves = self.get_moves_for_square((x,y))
                    moves.update(newmoves)
                # Mochiuma case
                elif self[x][y] == 0 and (y == 2 or y == 3) and len(mochilist) != 0:
                    for pieces in range len(mochilist):
                        moves.add((piece, x, y, 1))
        return list(moves)

    def has_legal_moves(self, color):
        mochilist = self.WhiteMochi if color == 1 else self.BlackMochi # given color's Mochiuma list
      
        for y in range(4):
            for x in range(3):
                if np.sign(self[x][y]) == color:
                    newmoves = self.get_moves_for_square((x,y))
                    if len(newmoves)>0:
                        return True
                # Mochiuma case
                elif self[x][y] == 0 and (y == 2 or y == 3) and len(mochilist) != 0:
                    return True
        return False

    def get_moves_for_square(self, square):
        """Returns all the legal moves using the piece on the square.
        Move are notated in tuple (piece, x, y, dest_x, dest_y, mochi)
        Mochi denotes whether the move is Mochiuma move or not. In mochi case x=y=0
        e.g. White lion from B-file, 1st rank to C-file, 2nd rank is (4, 1, 0, 2, 1, 0)
             Mochiuma Black Giraffe to B-file, 3rd rank is (-3, 0, 0, 1, 2, 1)
        """
        (x,y) = square
        piece = self[x][y]

        # determine the color and type of the piece.
        color = np.sign(piece)
        piece = abs(piece) if piece != -1 else 0

        # skip empty source squares.
        if color==0:
            return None

        # search all possible directions.
        moves = []
        for direction in self.__directions[piece]:
            move = self._discover_move(square, direction)
            if move:
                # print(square,move,direction)
                moves.append(move)

        # return the generated move list
        return moves

    def execute_move(self, move, color):
        """Perform the given move on the board.
        """
        # print(move)
        mochilist = self.WhiteMochi if color == 1 else self.BlackMochi # given color's Mochiuma list
        piece, dest_x, dest_y, mochi = move
        if piece == 1 or np.sign(self[dest_x][dest_y]) == -color:
            self.draw_counter = 0
        else:
            self.draw_counter += 1
        piece *= color
        
        # Mochiuma case
        if mochi:
            self[dest_x][dest_y] = piece
            mochilist.remove(piece)
            return
        else:
            self[x][y] = 0
            # Taking opponent's piece into Mochiuma list
            if self[dest_x][dest_y] != 0:
                mochilist.append(-self[dest_x][dest_y])
            self[dest_x][dest_y] = piece
            return

    def _discover_move(self, origin, direction):
        """ If moving the piece on origin in direction is a valid move, returns the move. If not, returns None.
        """
        x, y = origin
        dest_x, dest_y = [a + b for a, b in zip(origin, direction)]
        piece = self[x][y]

        if 0 <= dest_x < 3 and 0 <= dest_y < 4 and np.sign(self[dest_x][dest_y]) != np.sign(piece):
            return (piece, x, y, dest_x, dest_y, 0)
        else:
            return None

