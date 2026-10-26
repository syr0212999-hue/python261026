import random
import tkinter as tk

# 게임 보드 설정
COLS = 10
ROWS = 20
BLOCK = 30
WIDTH = COLS * BLOCK
HEIGHT = ROWS * BLOCK

# 블록 모양과 색상
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]],
}

COLORS = {
    'I': '#00E5FF',
    'J': '#4D79FF',
    'L': '#FFB74D',
    'O': '#FFD600',
    'S': '#66BB6A',
    'T': '#BA68C8',
    'Z': '#FF5252',
}


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title('Demo Tetris')
        self.root.resizable(False, False)

        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current = None
        self.next = self.create_piece()
        self.drop_speed = 500
        self.after_id = None

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='#111111', highlightthickness=0)
        self.canvas.pack(side='left', padx=10, pady=10)

        self.side = tk.Frame(root, bg='#222222', padx=15, pady=15)
        self.side.pack(side='left', fill='y')

        self.next_canvas = tk.Canvas(self.side, width=120, height=120, bg='#1a1a1a', highlightthickness=0)
        self.next_canvas.pack(pady=(0, 20))

        self.score_label = tk.Label(self.side, text='점수: 0', fg='white', bg='#222222', font=('Arial', 16, 'bold'))
        self.score_label.pack(anchor='w')

        self.info_label = tk.Label(
            self.side,
            text='← → 이동\n↑ 회전\n↓ 빠르게\nSpace 바로내리기',
            fg='white',
            bg='#222222',
            font=('Arial', 12),
            justify='left'
        )
        self.info_label.pack(anchor='w', pady=(20, 0))

        self.root.bind('<Left>', lambda event: self.move(-1, 0))
        self.root.bind('<Right>', lambda event: self.move(1, 0))
        self.root.bind('<Down>', lambda event: self.soft_drop())
        self.root.bind('<Up>', lambda event: self.rotate())
        self.root.bind('<space>', lambda event: self.hard_drop())
        self.root.bind('r', lambda event: self.restart())

        self.spawn_piece()
        self.draw()
        self.start_loop()

    def create_piece(self):
        name = random.choice(list(SHAPES.keys()))
        matrix = [row[:] for row in SHAPES[name]]
        return {'shape': name, 'matrix': matrix, 'x': COLS // 2 - len(matrix[0]) // 2, 'y': 0, 'color': COLORS[name]}

    def rotate_matrix(self, matrix):
        return [list(row) for row in zip(*matrix[::-1])]

    def spawn_piece(self):
        self.current = self.next
        self.current['x'] = COLS // 2 - len(self.current['matrix'][0]) // 2
        self.current['y'] = 0
        self.next = self.create_piece()

        if not self.is_valid_move(self.current['matrix'], self.current['x'], self.current['y']):
            self.game_over = True
            self.info_label.config(text='게임 오버\nR키를 눌러 다시 시작')
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def start_loop(self):
        if not self.game_over:
            self.after_id = self.root.after(self.drop_speed, self.tick)

    def tick(self):
        if self.game_over:
            return

        if self.is_valid_move(self.current['matrix'], self.current['x'], self.current['y'] + 1):
            self.current['y'] += 1
        else:
            self.lock_piece()

        self.draw()
        self.start_loop()

    def move(self, dx, dy):
        if self.game_over:
            return

        if self.is_valid_move(self.current['matrix'], self.current['x'] + dx, self.current['y'] + dy):
            self.current['x'] += dx
            self.current['y'] += dy
            self.draw()

    def soft_drop(self):
        if self.game_over:
            return
        if self.is_valid_move(self.current['matrix'], self.current['x'], self.current['y'] + 1):
            self.current['y'] += 1
        else:
            self.lock_piece()
        self.draw()

    def hard_drop(self):
        if self.game_over:
            return

        while self.is_valid_move(self.current['matrix'], self.current['x'], self.current['y'] + 1):
            self.current['y'] += 1
            self.score += 2

        self.lock_piece()
        self.score_label.config(text=f'점수: {self.score}')
        self.draw()

    def rotate(self):
        if self.game_over:
            return

        rotated = self.rotate_matrix(self.current['matrix'])
        x = self.current['x']

        # 회전 시 좌우 위치를 보정하여 가능한 위치 찾기
        for offset in (0, -1, 1, -2, 2):
            if self.is_valid_move(rotated, x + offset, self.current['y']):
                self.current['matrix'] = rotated
                self.current['x'] += offset
                self.draw()
                return

    def is_valid_move(self, matrix, x, y):
        for row_idx, row in enumerate(matrix):
            for col_idx, value in enumerate(row):
                if value == 0:
                    continue

                new_x = x + col_idx
                new_y = y + row_idx

                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False

                if new_y >= 0 and self.board[new_y][new_x] != 0:
                    return False

        return True

    def lock_piece(self):
        for row_idx, row in enumerate(self.current['matrix']):
            for col_idx, value in enumerate(row):
                if value == 0:
                    continue

                x = self.current['x'] + col_idx
                y = self.current['y'] + row_idx

                if y >= 0:
                    self.board[y][x] = self.current['color']

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        full_rows = []
        for y, row in enumerate(self.board):
            if all(cell != 0 for cell in row):
                full_rows.append(y)

        for y in reversed(full_rows):
            del self.board[y]
            self.board.insert(0, [0 for _ in range(COLS)])

        if full_rows:
            self.score += len(full_rows) * 100
            self.score_label.config(text=f'점수: {self.score}')

    def draw_block(self, canvas, x, y, color):
        canvas.create_rectangle(x * BLOCK, y * BLOCK, (x + 1) * BLOCK, (y + 1) * BLOCK,
                               fill=color, outline='#333333', width=1)

    def draw_board(self):
        self.canvas.delete('all')

        for y in range(ROWS):
            for x in range(COLS):
                if self.board[y][x] != 0:
                    self.draw_block(self.canvas, x, y, self.board[y][x])

        if self.current:
            for y, row in enumerate(self.current['matrix']):
                for x, block in enumerate(row):
                    if block:
                        bx = self.current['x'] + x
                        by = self.current['y'] + y
                        if by >= 0:
                            self.draw_block(self.canvas, bx, by, self.current['color'])

    def draw_next_piece(self):
        self.next_canvas.delete('all')

        matrix = self.next['matrix']
        offset_x = (4 - len(matrix[0])) // 2
        offset_y = (4 - len(matrix)) // 2

        for y, row in enumerate(matrix):
            for x, block in enumerate(row):
                if block:
                    self.next_canvas.create_rectangle(
                        (x + offset_x) * 25,
                        (y + offset_y) * 25,
                        (x + offset_x + 1) * 25,
                        (y + offset_y + 1) * 25,
                        fill=self.next['color'],
                        outline='#333333',
                        width=1,
                    )

    def draw(self):
        self.draw_board()
        self.draw_next_piece()

    def restart(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.next = self.create_piece()
        self.score_label.config(text='점수: 0')
        self.info_label.config(text='← → 이동\n↑ 회전\n↓ 빠르게\nSpace 바로내리기')
        self.spawn_piece()
        self.draw()
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.start_loop()


if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
