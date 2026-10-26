import random
import tkinter as tk
from tkinter import messagebox

# 설정
ROWS = 9
COLS = 9
MINES = 10
CELL_SIZE = 40
WINDOW_SIZE = CELL_SIZE * COLS

# 색상
BG = '#1e1e1e'
GRID = '#3a3a3a'
BUTTON_BG = '#dfe6e9'
BUTTON_HOVER = '#b2bec3'
OPEN_BG = '#f5f5f5'
FLAG_COLOR = '#ff7675'
MINE_COLOR = '#d63031'
TEXT_COLORS = {
    1: '#0984e3',
    2: '#00b894',
    3: '#fdcb6e',
    4: '#6c5ce7',
    5: '#e17055',
    6: '#00cec9',
    7: '#2d3436',
    8: '#636e72',
}


class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title('지뢰찾기')
        self.root.resizable(False, False)

        self.frame = tk.Frame(root, bg=BG)
        self.frame.pack()

        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.game_over = False
        self.first_click = True
        self.flags_left = MINES

        self.buttons = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                btn = tk.Button(
                    self.frame,
                    width=2,
                    height=1,
                    font=('Arial', 14, 'bold'),
                    bg=BUTTON_BG,
                    activebackground=BUTTON_HOVER,
                    relief='raised',
                    command=lambda rr=r, cc=c: self.click(rr, cc),
                )
                btn.bind('<Button-3>', lambda event, rr=r, cc=c: self.toggle_flag(rr, cc))
                btn.grid(row=r, column=c)
                row.append(btn)
            self.buttons.append(row)

        self.status_label = tk.Label(root, text=f'남은 깃발: {self.flags_left}', bg=BG, fg='white', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=(10, 0))

        self.reset_button = tk.Button(root, text='다시 시작', command=self.reset_game, font=('Arial', 11, 'bold'))
        self.reset_button.pack(pady=(5, 10))

        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.game_over = False
        self.first_click = True
        self.flags_left = MINES
        self.status_label.config(text=f'남은 깃발: {self.flags_left}')

        for r in range(ROWS):
            for c in range(COLS):
                self.buttons[r][c].config(text='', bg=BUTTON_BG, relief='raised', state='normal', fg='black')

    def place_mines(self, avoid_r, avoid_c):
        positions = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) != (avoid_r, avoid_c)]
        random.shuffle(positions)

        for r, c in positions[:MINES]:
            self.board[r][c] = -1

        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and self.board[nr][nc] == -1:
                            count += 1
                self.board[r][c] = count

    def click(self, r, c):
        if self.game_over:
            return

        if self.flagged[r][c]:
            return

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False

        if self.board[r][c] == -1:
            self.reveal_mines()
            self.game_over = True
            messagebox.showinfo('게임 오버', '지뢰를 밟았습니다!')
            return

        self.expand_empty(r, c)
        self.check_win()

    def toggle_flag(self, r, c):
        if self.game_over:
            return

        if self.revealed[r][c]:
            return

        if self.flagged[r][c]:
            self.flagged[r][c] = False
            self.flags_left += 1
            self.buttons[r][c].config(text='', bg=BUTTON_BG)
        else:
            if self.flags_left <= 0:
                return
            self.flagged[r][c] = True
            self.flags_left -= 1
            self.buttons[r][c].config(text='🚩', bg='#ffeaa7', fg=FLAG_COLOR)

        self.status_label.config(text=f'남은 깃발: {self.flags_left}')

    def reveal_mines(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == -1:
                    self.buttons[r][c].config(text='💣', bg=MINE_COLOR, fg='white')
                elif self.board[r][c] > 0 and not self.flagged[r][c]:
                    self.buttons[r][c].config(text=str(self.board[r][c]), bg=OPEN_BG, fg=TEXT_COLORS[self.board[r][c]])

    def expand_empty(self, r, c):
        stack = [(r, c)]

        while stack:
            rr, cc = stack.pop()
            if self.revealed[rr][cc]:
                continue
            self.revealed[rr][cc] = True
            self.buttons[rr][cc].config(bg=OPEN_BG, relief='sunken')

            if self.board[rr][cc] != 0:
                self.buttons[rr][cc].config(text=str(self.board[rr][cc]), fg=TEXT_COLORS.get(self.board[rr][cc], 'black'))
                continue

            self.buttons[rr][cc].config(text='', bg=OPEN_BG)

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                        if self.board[nr][nc] == -1:
                            continue
                        stack.append((nr, nc))

    def check_win(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return

        self.game_over = True
        messagebox.showinfo('승리!', '모든 지뢰를 피했습니다!')


if __name__ == '__main__':
    root = tk.Tk()
    app = Minesweeper(root)
    root.mainloop()
