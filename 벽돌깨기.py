import random
import tkinter as tk


WIDTH = 800
HEIGHT = 600
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 14
PADDLE_SPEED = 12
BALL_RADIUS = 9
BRICK_ROWS = 6
BRICK_COLUMNS = 10
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 7
BRICK_LEFT = (WIDTH - (BRICK_COLUMNS * BRICK_WIDTH + (BRICK_COLUMNS - 1) * BRICK_GAP)) // 2
BRICK_TOP = 65
ITEM_SIZE = 18
ITEM_SPEED = 4
BULLET_SPEED = 12

BRICK_COLORS = [
    "#FF1744",
    "#FF9100",
    "#FFEA00",
    "#00E676",
    "#00B0FF",
    "#D500F9",
]


class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("블럭깨기")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#10152b",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys_down = set()
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.canvas.bind("<Motion>", self.move_paddle_with_mouse)

        self.restart()
        self.tick()

    def restart(self):
        self.paddle_x = WIDTH / 2
        self.paddle_y = HEIGHT - 45
        self.ball_x = WIDTH / 2
        self.ball_y = self.paddle_y - BALL_RADIUS - 2
        self.ball_dx = 5
        self.ball_dy = -7
        self.lives = 3
        self.score = 0
        self.ammo = 0
        self.game_over = False
        self.won = False
        self.bricks = []
        self.items = []
        self.bullets = []
        self.next_shot = 0
        self.keys_down.clear()

        for row in range(BRICK_ROWS):
            for column in range(BRICK_COLUMNS):
                x1 = BRICK_LEFT + column * (BRICK_WIDTH + BRICK_GAP)
                y1 = BRICK_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
                self.bricks.append(
                    {
                        "x1": x1,
                        "y1": y1,
                        "x2": x1 + BRICK_WIDTH,
                        "y2": y1 + BRICK_HEIGHT,
                        "color": BRICK_COLORS[row],
                    }
                )
        self.draw()

    def key_down(self, event):
        key = event.keysym.lower()
        if key == "r" and (self.game_over or self.won):
            self.restart()
            return
        if key == "space":
            self.shoot()
        self.keys_down.add(key)

    def key_up(self, event):
        self.keys_down.discard(event.keysym.lower())

    def move_paddle_with_mouse(self, event):
        self.paddle_x = max(
            PADDLE_WIDTH / 2,
            min(WIDTH - PADDLE_WIDTH / 2, event.x),
        )

    def shoot(self):
        if self.game_over or self.won or self.ammo <= 0:
            return

        now = self.root.tk.call("clock", "milliseconds")
        if int(now) < self.next_shot:
            return

        self.next_shot = int(now) + 250
        self.ammo -= 1
        self.bullets.append(
            {"x": self.paddle_x, "y": self.paddle_y - PADDLE_HEIGHT / 2}
        )

    @staticmethod
    def overlaps_circle_rect(cx, cy, radius, brick):
        closest_x = max(brick["x1"], min(cx, brick["x2"]))
        closest_y = max(brick["y1"], min(cy, brick["y2"]))
        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy <= radius * radius

    def move_ball(self):
        previous_x = self.ball_x
        previous_y = self.ball_y
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_x - BALL_RADIUS <= 0 or self.ball_x + BALL_RADIUS >= WIDTH:
            self.ball_dx *= -1
            self.ball_x = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, self.ball_x))
        if self.ball_y - BALL_RADIUS <= 0:
            self.ball_dy *= -1
            self.ball_y = BALL_RADIUS

        paddle_left = self.paddle_x - PADDLE_WIDTH / 2
        paddle_right = self.paddle_x + PADDLE_WIDTH / 2
        paddle_top = self.paddle_y - PADDLE_HEIGHT / 2
        if (
            self.ball_dy > 0
            and self.ball_y + BALL_RADIUS >= paddle_top
            and self.ball_y - BALL_RADIUS <= self.paddle_y + PADDLE_HEIGHT / 2
            and paddle_left <= self.ball_x <= paddle_right
        ):
            offset = (self.ball_x - self.paddle_x) / (PADDLE_WIDTH / 2)
            self.ball_dx = offset * 6
            self.ball_dy = -max(4, 7 - abs(self.ball_dx) * 0.35)
            self.ball_y = paddle_top - BALL_RADIUS

        for brick in self.bricks[:]:
            if not self.overlaps_circle_rect(
                self.ball_x, self.ball_y, BALL_RADIUS, brick
            ):
                continue

            self.bricks.remove(brick)
            self.score += 10
            if previous_y + BALL_RADIUS <= brick["y1"] or previous_y - BALL_RADIUS >= brick["y2"]:
                self.ball_dy *= -1
            else:
                self.ball_dx *= -1

            if random.random() < 0.25:
                self.items.append(
                    {
                        "x": (brick["x1"] + brick["x2"]) / 2,
                        "y": (brick["y1"] + brick["y2"]) / 2,
                    }
                )
            break

        if self.ball_y - BALL_RADIUS > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_x = WIDTH / 2
                self.ball_y = self.paddle_y - BALL_RADIUS - 2
                self.ball_dx = random.choice([-5, 5])
                self.ball_dy = -7

    def update_items_and_bullets(self):
        paddle_left = self.paddle_x - PADDLE_WIDTH / 2
        paddle_right = self.paddle_x + PADDLE_WIDTH / 2
        for item in self.items[:]:
            item["y"] += ITEM_SPEED
            if (
                item["y"] + ITEM_SIZE / 2 >= self.paddle_y - PADDLE_HEIGHT / 2
                and item["y"] - ITEM_SIZE / 2 <= self.paddle_y + PADDLE_HEIGHT / 2
                and paddle_left <= item["x"] <= paddle_right
            ):
                self.items.remove(item)
                self.ammo += 5
            elif item["y"] - ITEM_SIZE / 2 > HEIGHT:
                self.items.remove(item)

        for bullet in self.bullets[:]:
            bullet["y"] -= BULLET_SPEED
            if bullet["y"] < 0:
                self.bullets.remove(bullet)
                continue

            for brick in self.bricks[:]:
                if (
                    brick["x1"] <= bullet["x"] <= brick["x2"]
                    and brick["y1"] <= bullet["y"] <= brick["y2"]
                ):
                    self.bricks.remove(brick)
                    self.bullets.remove(bullet)
                    self.score += 10
                    if random.random() < 0.25:
                        self.items.append(
                            {
                                "x": (brick["x1"] + brick["x2"]) / 2,
                                "y": (brick["y1"] + brick["y2"]) / 2,
                            }
                        )
                    break

    def tick(self):
        if not self.game_over and not self.won:
            if "left" in self.keys_down or "a" in self.keys_down:
                self.paddle_x = max(
                    PADDLE_WIDTH / 2, self.paddle_x - PADDLE_SPEED
                )
            if "right" in self.keys_down or "d" in self.keys_down:
                self.paddle_x = min(
                    WIDTH - PADDLE_WIDTH / 2, self.paddle_x + PADDLE_SPEED
                )

            self.move_ball()
            self.update_items_and_bullets()
            if not self.bricks:
                self.won = True

        self.draw()
        self.root.after(16, self.tick)

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            12,
            18,
            anchor="w",
            fill="white",
            font=("맑은 고딕", 12, "bold"),
            text=f"점수: {self.score}    목숨: {self.lives}    탄환: {self.ammo}",
        )

        for brick in self.bricks:
            self.canvas.create_rectangle(
                brick["x1"],
                brick["y1"],
                brick["x2"],
                brick["y2"],
                fill=brick["color"],
                outline="#ffffff",
                width=1,
            )

        paddle_left = self.paddle_x - PADDLE_WIDTH / 2
        paddle_right = self.paddle_x + PADDLE_WIDTH / 2
        self.canvas.create_rectangle(
            paddle_left,
            self.paddle_y - PADDLE_HEIGHT / 2,
            paddle_right,
            self.paddle_y + PADDLE_HEIGHT / 2,
            fill="#80d8ff",
            outline="#ffffff",
            width=2,
        )
        self.canvas.create_oval(
            self.ball_x - BALL_RADIUS,
            self.ball_y - BALL_RADIUS,
            self.ball_x + BALL_RADIUS,
            self.ball_y + BALL_RADIUS,
            fill="#ffffff",
            outline="#ffe082",
            width=2,
        )

        for item in self.items:
            x, y = item["x"], item["y"]
            self.canvas.create_oval(
                x - ITEM_SIZE / 2,
                y - ITEM_SIZE / 2,
                x + ITEM_SIZE / 2,
                y + ITEM_SIZE / 2,
                fill="#00e676",
                outline="#ffffff",
                width=2,
            )
            self.canvas.create_text(x, y, text="★", fill="#123c2a", font=("Arial", 10, "bold"))

        for bullet in self.bullets:
            self.canvas.create_rectangle(
                bullet["x"] - 3,
                bullet["y"] - 8,
                bullet["x"] + 3,
                bullet["y"] + 8,
                fill="#ffeb3b",
                outline="#ffffff",
            )

        if self.game_over or self.won:
            message = "승리!" if self.won else "게임 오버"
            self.canvas.create_rectangle(
                0, HEIGHT / 2 - 48, WIDTH, HEIGHT / 2 + 48, fill="#000000"
            )
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2 - 12,
                text=message,
                fill="#ffea00" if self.won else "#ff5252",
                font=("맑은 고딕", 28, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2 + 24,
                text="R 키를 눌러 다시 시작",
                fill="white",
                font=("맑은 고딕", 13),
            )


if __name__ == "__main__":
    root = tk.Tk()
    BreakoutGame(root)
    root.mainloop()
