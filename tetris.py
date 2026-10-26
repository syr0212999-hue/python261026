import random
import tkinter as tk

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 28
NEXT_SIZE = 4
SIDE_PANEL = 180
WINDOW_WIDTH = BOARD_WIDTH * BLOCK_SIZE + SIDE_PANEL
WINDOW_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

COLORS = {
    "I": "#00E5FF",
    "O": "#FFD600",
    "T": "#D500F9",
    "S": "#69F0AE",
    "Z": "#FF5252",
    "J": "#448AFF",
    "L": "#FFB74D",
}


class Piece:
    def __init__(self, shape_name):
        self.name = shape_name
        self.matrix = [row[:] for row in SHAPES[shape_name]]
        self.color = COLORS[shape_name]
        self.x = BOARD_WIDTH // 2 - len(self.matrix[0]) // 2
        self.y = -1


def rotate_matrix(matrix):
    return [list(row) for row in zip(*matrix[::-1])]


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("테트리스")
        self.root.resizable(False, False)

        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.next_piece = self.create_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False

        self.canvas = tk.Canvas(
            root,
            width=BOARD_WIDTH * BLOCK_SIZE,
            height=BOARD_HEIGHT * BLOCK_SIZE,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.next_canvas = tk.Canvas(
            root,
            width=NEXT_SIZE * BLOCK_SIZE,
            height=NEXT_SIZE * BLOCK_SIZE,
            bg="#1a1a1a",
            highlightthickness=0,
        )
        self.next_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.score_label = tk.Label(root, text="점수: 0", font=("맑은 고딕", 14, "bold"), fg="white", bg="#2b2b2b")
        self.score_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        self.lines_label = tk.Label(root, text="줄: 0", font=("맑은 고딕", 12), fg="white", bg="#2b2b2b")
        self.lines_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        self.info_label = tk.Label(root, text="방향키로 이동\n스페이스: 빠르게 내리기\nR: 다시 시작", font=("맑은 고딕", 11), fg="#dfe6e9", bg="#2b2b2b", justify="left")
        self.info_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        self.root.bind("<Left>", lambda e: self.move_piece(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_piece(1, 0))
        self.root.bind("<Down>", lambda e: self.soft_drop())
        self.root.bind("<Up>", lambda e: self.rotate_piece())
        self.root.bind("<space>", lambda e: self.hard_drop())
        self.root.bind("<r>", lambda e: self.restart_game())
        self.root.bind("<KeyPress-q>", lambda e: self.root.destroy())

        self.drop_speed = 500
        self.after_id = None
        self.spawn_piece()
        self.draw()
        self.start_loop()

    def create_piece(self):
        shape_name = random.choice(list(SHAPES.keys()))
        return Piece(shape_name)

    def start_loop(self):
        if self.game_over:
            return
        self.after_id = self.root.after(self.drop_speed, self.tick)

    def tick(self):
        if self.game_over:
            return
        if not self.move_piece(0, 1):
            self.lock_piece()
        self.draw()
        self.start_loop()

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.current_piece.x = BOARD_WIDTH // 2 - len(self.current_piece.matrix[0]) // 2
        self.current_piece.y = -1
        self.next_piece = self.create_piece()

        if not self.can_place(self.current_piece):
            self.game_over = True
            self.info_label.config(text="게임 오버!\nR 키로 다시 시작")

    def can_place(self, piece, dx=0, dy=0, matrix=None):
        matrix = piece.matrix if matrix is None else matrix
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                if value == 0:
                    continue
                x = piece.x + col_index + dx
                y = piece.y + row_index + dy

                if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                    return False
                if y >= 0 and self.board[y][x] != 0:
                    return False
        return True

    def move_piece(self, dx, dy):
        if self.game_over:
            return False
        if self.can_place(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            self.draw()
            return True

        if dy > 0:
            self.lock_piece()
            self.draw()
            return False
        return False

    def soft_drop(self):
        if self.game_over:
            return
        if not self.move_piece(0, 1):
            self.lock_piece()
        self.draw()

    def hard_drop(self):
        if self.game_over:
            return
        while self.move_piece(0, 1):
            self.score += 2
        self.score_label.config(text=f"점수: {self.score}")
        self.draw()

    def rotate_piece(self):
        if self.game_over:
            return
        rotated = rotate_matrix(self.current_piece.matrix)
        original_x = self.current_piece.x

        for offset in (0, -1, 1, -2, 2):
            if self.can_place(self.current_piece, offset, 0, rotated):
                self.current_piece.matrix = rotated
                self.current_piece.x += offset
                self.draw()
                return

        self.current_piece.x = original_x

    def lock_piece(self):
        for row_index, row in enumerate(self.current_piece.matrix):
            for col_index, value in enumerate(row):
                if value == 0:
                    continue
                x = self.current_piece.x + col_index
                y = self.current_piece.y + row_index
                if y >= 0:
                    self.board[y][x] = self.current_piece.color

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        rows_to_remove = []
        for index, row in enumerate(self.board):
            if all(cell != 0 for cell in row):
                rows_to_remove.append(index)

        for row_index in rows_to_remove:
            del self.board[row_index]
            self.board.insert(0, [0 for _ in range(BOARD_WIDTH)])

        if rows_to_remove:
            self.lines += len(rows_to_remove)
            self.level = self.lines // 10 + 1
            self.score += [0, 100, 300, 500, 800][len(rows_to_remove)] * self.level
            self.drop_speed = max(100, 500 - (self.level - 1) * 40)

        self.score_label.config(text=f"점수: {self.score}")
        self.lines_label.config(text=f"줄: {self.lines}")

    def draw_block(self, canvas, x, y, color):
        x0 = x * BLOCK_SIZE
        y0 = y * BLOCK_SIZE
        x1 = x0 + BLOCK_SIZE
        y1 = y0 + BLOCK_SIZE
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#444444", width=1)

    def draw_grid(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                self.canvas.create_rectangle(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    (x + 1) * BLOCK_SIZE,
                    (y + 1) * BLOCK_SIZE,
                    fill="#111111",
                    outline="#1f1f1f",
                    width=1,
                )

    def draw_piece_preview(self):
        self.next_canvas.delete("all")
        for y in range(NEXT_SIZE):
            for x in range(NEXT_SIZE):
                self.next_canvas.create_rectangle(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    (x + 1) * BLOCK_SIZE,
                    (y + 1) * BLOCK_SIZE,
                    fill="#1a1a1a",
                    outline="#2a2a2a",
                    width=1,
                )

        if self.next_piece is None:
            return

        matrix = self.next_piece.matrix
        offset_x = (NEXT_SIZE - len(matrix[0])) // 2
        offset_y = (NEXT_SIZE - len(matrix)) // 2
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                if value:
                    self.draw_block_on_canvas(self.next_canvas, offset_x + col_index, offset_y + row_index, self.next_piece.color)

    def draw_block_on_canvas(self, canvas, x, y, color):
        x0 = x * BLOCK_SIZE
        y0 = y * BLOCK_SIZE
        x1 = x0 + BLOCK_SIZE
        y1 = y0 + BLOCK_SIZE
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#444444", width=1)

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()

        for y, row in enumerate(self.board):
            for x, value in enumerate(row):
                if value:
                    self.draw_block(self.canvas, x, y, value)

        if self.current_piece:
            for row_index, row in enumerate(self.current_piece.matrix):
                for col_index, value in enumerate(row):
                    if value:
                        board_x = self.current_piece.x + col_index
                        board_y = self.current_piece.y + row_index
                        if board_y >= 0:
                            self.draw_block(self.canvas, board_x, board_y, self.current_piece.color)

        self.draw_piece_preview()

    def restart_game(self):
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.drop_speed = 500
        self.score_label.config(text="점수: 0")
        self.lines_label.config(text="줄: 0")
        self.info_label.config(text="방향키로 이동\n스페이스: 빠르게 내리기\nR: 다시 시작")
        self.next_piece = self.create_piece()
        self.spawn_piece()
        self.draw()
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.start_loop()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#2b2b2b")
    game = Tetris(root)
    root.mainloop()
