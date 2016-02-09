import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty

from game import *

class TetrivyApp(App):
    game = ObjectProperty(None)

    def build(self):
        self.game = GameScreen()
        return self.game

class GameScreen(BoxLayout):
    board = ObjectProperty(None)
    sidebar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.game_state = GameState()
        self.board.set_game_state(self.game_state)
        self.sidebar.set_game_state(self.game_state)
        self.bind(pos=self.redraw)
        self.bind(size=self.redraw)

    def start_game(self, *args):
        Clock.unschedule(self.tick)
        self.game_state.reset()
        self.game_state.start()
        self.tick()

    def tick(self, *args):
        if not self.game_state.is_game_over():
            self.game_state.tick()
            delay = max(10-self.game_state.level, 1) * .05
            Clock.schedule_once(self.tick, delay)
        self.redraw()

    def redraw(self, *args):
        self.sidebar.refresh(self.game_state)
        self.board.redraw()

    def calculate_board_size(self):
        height = self.board.height - 20
        width = height / 2
        if width > self.board.width:
            width = self.board.width - 20
            height = self.board.width * 2
            x = 0
            y = (self.board.height - height) / 2

        x = (self.board.width - width) / 2
        y = (self.board.height - height) / 2
        return x, y, width, height

    def block_size(self):
        board_x, board_y, board_width, board_height = \
            self.calculate_board_size()
        block_width = board_width / GRID_WIDTH - 1
        block_height = board_height / (GRID_HEIGHT-2) - 1
        return block_width, block_height

class Board(Widget):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.bind(pos=self.redraw)
        self.bind(size=self.redraw)
        self.game_state = None

    def set_game_state(self, game_state):
        self.game_state = game_state

    def on_touch_down(self, event):
        if not self.game_state or self.game_state.status != GameStatus.ACTIVE:
            return
        if event.x > self.width * .75:
            self.game_state.move_right()
        elif event.x < self.width * .25:
            self.game_state.move_left()
        elif event.y < self.height * .25:
            self.game_state.move_down()
        else:
            self.game_state.rotate()
        self.redraw()

    def redraw(self, *args):
        self.canvas.before.clear()
        self.canvas.clear()
        board_x, board_y, board_width, board_height = self.parent.calculate_board_size()
        block_width, block_height = self.parent.block_size()
        
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            Line(width=2.,
                 rectangle=(board_x-2, board_y-2, board_width+3,
                 board_height+3))

        if not self.game_state:
            return

        with self.canvas:
            cur_y = board_y + (GRID_HEIGHT-3) * (block_height+1)
            for row in self.game_state.grid[2:]:
                cur_x = board_x
                for col in row:
                    Color(*BlockColor.to_color(col))
                    Rectangle(pos=(cur_x, cur_y),
                              size=(block_width, block_height))
                    cur_x += block_width + 1
                cur_y -= block_height + 1

            current_piece = self.game_state.current_piece
            if not current_piece:
                return
            squares = current_piece.shape()
            Color(*BlockColor.to_color(current_piece.piece_type))
            for square in squares:
                row, col = square
                if row < 2:
                    continue
                Rectangle(pos=(board_x + col * (block_width+1),
                             board_y + (GRID_HEIGHT-row-1) * (block_height+1)),
                          size=(block_width, block_height))

        if self.game_state.status == GameStatus.GAME_OVER:
            with self.canvas:
                Color(0, 0, 0, 0.5)
                Rectangle(pos=(board_x, board_y),
                          size=(board_width, board_height))


class Sidebar(BoxLayout):
    score = ObjectProperty(None)
    level = ObjectProperty(None)
    lines_cleared = ObjectProperty(None)
    next_piece = ObjectProperty(None)
    start_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.bind(pos=self.refresh)
        self.bind(size=self.refresh)
        self.game_state = None

    def set_game_state(self, game_state):
        self.game_state = game_state

    def refresh(self, *args):
        self.score.text = str(self.game_state.score)
        self.level.text = str(self.game_state.level)
        self.lines_cleared.text = str(self.game_state.lines_cleared)
        self.render_next_piece()
        if self.game_state.status == GameStatus.ACTIVE:
            self.start_button.disabled = True
        else:
            self.start_button.disabled = False

    def render_next_piece(self):
        next_piece = self.next_piece
        next_piece.canvas.before.clear()
        next_piece.canvas.clear()
        if not self.game_state or self.game_state.status != GameStatus.ACTIVE:
            return
        block_width, block_height = self.parent.block_size()

        # A little smaller to fit in the sidebar
        block_width *= .7
        block_height *= .7

        # Dimensions of the preview box (not using the full widget space)
        width = (block_width+1)*4
        height = (block_height+1)*3
        x = next_piece.x + (next_piece.width - width)/2
        y = next_piece.y + next_piece.height - height

        with next_piece.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            Line(width=2., rectangle=(x-2, y-2, width+4, height+4))
            Color(0., 0., 0., 1)
            Rectangle(pos=(x, y), size=(width, height))

        with next_piece.canvas:
            next_piece_type = self.game_state.piece_generator.next_piece_type()
            Color(*BlockColor.to_color(next_piece_type))
            for square in PIECE_GEOMETRY[next_piece_type][0]:
                row, col = square[0]+1, square[1]+1
                Rectangle(pos=(x + col * (block_width+1),
                               y + (2-row) * (block_height+1)),
                          size=(block_width, block_height))


if __name__ == '__main__':
    TetrivyApp().run()
