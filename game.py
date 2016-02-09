# Non-platform-specific game logic.

from random import shuffle

GRID_WIDTH = 10
GRID_HEIGHT = 22

class BlockColor:
    EMPTY = 0
    CYAN = 1
    YELLOW = 2
    PURPLE = 3
    GREEN = 4
    RED = 5
    BLUE = 6
    ORANGE = 7

    @staticmethod
    def to_color(block_color):
        return {
            BlockColor.EMPTY: (0, 0, 0, 1),
            BlockColor.CYAN: (0, 1., 1., 1.),
            BlockColor.YELLOW: (1., 1., 0, 1.),
            BlockColor.PURPLE: (1., 0, 1., 1.),
            BlockColor.GREEN: (0, 1., 0, 1.),
            BlockColor.RED: (1., 0, 0, 1.),
            BlockColor.BLUE: (0, 0, 1., 1.),
            BlockColor.ORANGE: (1., 0.5, 0, 1.),
        }[block_color]

class PieceType:
    I = BlockColor.CYAN
    O = BlockColor.YELLOW
    T = BlockColor.PURPLE
    S = BlockColor.GREEN
    Z = BlockColor.RED
    J = BlockColor.BLUE
    L = BlockColor.ORANGE

class Orientation:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

PIECE_GEOMETRY = {
    PieceType.I: [
        [[ 0, -1], [ 0,  0], [ 0,  1], [ 0,  2]],
        [[-1,  1], [ 0,  1], [ 1,  1], [ 2,  1]],
        [[ 1, -1], [ 1,  0], [ 1,  1], [ 1,  2]],
        [[-1,  0], [ 0,  0], [ 1,  0], [ 2,  0]],
    ],
    PieceType.O: [
        [[-1,  0], [-1,  1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [-1,  1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [-1,  1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [-1,  1], [ 0,  0], [ 0,  1]],
    ],
    PieceType.T: [
        [[-1,  0], [ 0, -1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [ 0,  0], [ 0,  1], [ 1,  0]],
        [[ 0, -1], [ 0,  0], [ 0,  1], [ 1,  0]],
        [[-1,  0], [ 0, -1], [ 0,  0], [ 1,  0]],
    ],
    PieceType.S: [
        [[-1,  0], [-1,  1], [ 0, -1], [ 0,  0]],
        [[-1,  0], [ 0,  0], [ 0,  1], [ 1,  1]],
        [[ 0,  0], [ 0,  1], [ 1, -1], [ 1,  0]],
        [[-1, -1], [ 0, -1], [ 0,  0], [ 1,  0]],
    ],
    PieceType.Z: [
        [[-1, -1], [-1,  0], [ 0,  0], [ 0,  1]],
        [[-1,  1], [ 0,  0], [ 0,  1], [ 1,  0]],
        [[ 0, -1], [ 0,  0], [ 1,  0], [ 1,  1]],
        [[-1,  0], [ 0, -1], [ 0,  0], [ 1, -1]],
    ],
    PieceType.J: [
        [[-1, -1], [ 0, -1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [-1,  1], [ 0,  0], [ 1,  0]],
        [[ 0, -1], [ 0,  0], [ 0,  1], [ 1,  1]],
        [[-1,  0], [ 1, -1], [ 0,  0], [ 1,  0]],
    ],
    PieceType.L: [
        [[-1,  1], [ 0, -1], [ 0,  0], [ 0,  1]],
        [[-1,  0], [ 0,  0], [ 1,  0], [ 1,  1]],
        [[ 0, -1], [ 0,  0], [ 0,  1], [ 1, -1]],
        [[-1, -1], [-1,  0], [ 0,  0], [ 1,  0]],
    ],
}

class Piece:
    def __init__(self, piece_type):
        self.piece_type = piece_type
        self.row = 0
        self.col = GRID_WIDTH // 2 - 1
        self.orientation = Orientation.UP

    def color(self):
        return BlockColor.to_color(self.piece_type)

    def rotate(self, backward=False):
        direction = -1 if backward else 1
        self.orientation = (self.orientation + direction) % 4

    def shape(self):
        "Returns a list of coordinates describing the shape."
        row = self.row
        col = self.col
        geometry = PIECE_GEOMETRY[self.piece_type][self.orientation]
        return map(lambda s: [row+s[0], col+s[1]], geometry)

class PieceGenerator:
    def __init__(self):
        self.bag = self.new_bag()

    def new_bag(self):
        bag = [PieceType.I, PieceType.O, PieceType.T, PieceType.S,
               PieceType.Z, PieceType.J, PieceType.L]
        shuffle(bag)
        return bag

    def next_piece_type(self):
        return self.bag[0]

    def take_next_piece(self):
        piece_type = self.bag.pop(0)
        if not self.bag:
            self.bag = self.new_bag()
        return Piece(piece_type)

class GameStatus:
    INIT = 0
    ACTIVE = 1
    GAME_OVER = 2

class GameState:
    def __init__(self):
        self.reset()

    def start(self):
        if self.status != GameStatus.INIT:
            raise Exception("Cannot start game that isn't in INIT state.")
        self.status = GameStatus.ACTIVE

    def reset(self):
        self.piece_generator = PieceGenerator()
        self.grid = []
        for i in range(0, GRID_HEIGHT):
            self.grid.append([BlockColor.EMPTY] * GRID_WIDTH)
        self.current_piece = None
        self.level = 0
        self.score = 0
        self.lines_cleared = 0
        self.status = GameStatus.INIT

    def is_game_over(self):
        return self.status == GameStatus.GAME_OVER

    def tick(self):
        if self.status != GameStatus.ACTIVE:
            raise Exception("Cannot tick a game that isn't running.")
        if self.current_piece:
            self.move_down()
        if not self.current_piece:
            self.current_piece = self.piece_generator.take_next_piece()
            if self.check_collision():
                print("Game over")
                self.do_game_over()

    def move_left(self):
        self.current_piece.col -= 1
        if self.check_collision():
            self.current_piece.col += 1

    def move_right(self):
        self.current_piece.col += 1
        if self.check_collision():
            self.current_piece.col -= 1

    def move_down(self):
        self.current_piece.row += 1
        if self.check_collision():
            self.current_piece.row -= 1
            self.affix_piece()
            self.clear_lines()
            self.current_piece = None
            self.tick()

    def rotate(self):
        self.current_piece.rotate()
        if self.check_collision():
            self.current_piece.rotate(backward=True)

    def check_collision(self):
        collision = False
        for square in self.current_piece.shape():
            row, col = square
            # Ignore "collisions" with the top of grid
            if row < 0:
                continue
            elif row >= GRID_HEIGHT:
                collision = True
                break
            elif col >= GRID_WIDTH or col < 0:
                collision = True
                break
            elif self.grid[row][col] != BlockColor.EMPTY:
                collision = True
                break
        return collision

    def affix_piece(self):
        for square in self.current_piece.shape():
            row, col = square
            self.grid[row][col] = self.current_piece.piece_type

    def clear_lines(self):
        rows_to_remove = []
        for row in self.grid:
            if all(row):
                rows_to_remove.append(row)
        for row in rows_to_remove:
            self.grid.remove(row)
        lines = len(rows_to_remove)
        self.lines_cleared += lines
        for i in range(0, lines):
            self.grid.insert(0, [BlockColor.EMPTY] * GRID_WIDTH)
        self.score += [0, 40, 100, 300, 1200][lines] * (self.level+1)
        self.level = self.lines_cleared // 10

    def do_game_over(self):
        self.status = GameStatus.GAME_OVER
