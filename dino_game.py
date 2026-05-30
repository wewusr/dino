import curses
import random
import time
import os
import json

# === SPRITES ===

DINO_RUN1 = [
    "      ███████ ",
    "      ████▒███",
    "      ████████",
    "    ███████   ",
    "  ███████████ ",
    "  ██████████  ",
    "   ████████   ",
    "    █   █▄    ",
]

DINO_RUN2 = [
    "      ███████ ",
    "      ████▒███",
    "      ████████",
    "    ███████   ",
    "  ███████████ ",
    "  ██████████  ",
    "   ████████   ",
    "    █▄  █     ",
]

DINO_JUMP_SPRITE = [
    "      ███████ ",
    "      ████▒███",
    "      ████████",
    "    ███████   ",
    "  ███████████ ",
    "  ██████████  ",
    "   ████████   ",
    "    █▄  █▄    ",
]

DINO_DEAD = [
    "      ███████ ",
    "      ████x███",
    "      ████████",
    "    ███████   ",
    "  ███████████ ",
    "  ██████████  ",
    "   ████████   ",
    "    █▄  █▄    ",
]

CACTUS_SMALL = [
    "  █  ",
    " ▐█  ",
    " ▐█▌ ",
    "  █  ",
    "  █  ",
]

CACTUS_LARGE = [
    "  █   ",
    " ▐█ █ ",
    " ▐███ ",
    "  █▐  ",
    "  █   ",
    "  █   ",
]

CACTUS_CLUSTER = [
    "  █  █  ",
    " ▐█ ▐█  ",
    " ▐█▌▐█▌ ",
    "  █  █  ",
    "  █  █  ",
]

CACTUS_TALL = [
    "  █  ",
    " ▐█▌ ",
    " ▐█▌ ",
    " ▐█▌ ",
    "  █  ",
    "  █  ",
    "  █  ",
]

CACTUS_WAVY = [
    "   █  ",
    "  ▐█  ",
    " ▐█▌  ",
    "  █▌  ",
    "  ▐█  ",
    "  █   ",
]

CACTUS_BLOSSOM = [
    "  ✿  ",
    "  █  ",
    " ▐█▌ ",
    " ▐█▌ ",
    "  █  ",
    "  █  ",
]

BIRD_UP = [
    " \\\\    ",
    "  \\\\   ",
    "==={>  ",
    "       ",
]

BIRD_DOWN = [
    "       ",
    "==={>  ",
    "  //   ",
    " //    ",
]

CLOUD = [
    "   .-~~~-.  ",
    " .~       ~.",
    "~           ~",
]

MOUNTAIN = [
    "         /\\         ",
    "        /  \\        ",
    "       / /\\ \\       ",
    "      / /  \\ \\      ",
    "     / /    \\ \\     ",
    "    / /  /\\  \\ \\    ",
    "   /_/  /  \\  \\_\\   ",
    "       /    \\       ",
    "______/      \\______",
]

STAR_CHARS = [".", "*", "+", "·"]

COIN = [
    " ○ ",
    "◉◉◉",
    " ○ ",
]

SHIELD_ICON = [
    " ◇ ",
    "◇◇◇",
    " ◇ ",
]

MAGNET_ICON = [
    "╔═╗",
    "║M║",
    "╚═╝",
]

SLOW_ICON = [
    "█▀█",
    " █ ",
    "█▄█",
]

SUN = [
    "    \\ | /    ",
    "   - (☀) -   ",
    "    / | \\    ",
]

MOON = [
    "   ,-'\"`-.   ",
    "  /       \\  ",
    " |   ☾     | ",
    "  \\       /  ",
    "   `-...-'   "
]

# Flawlessly aligned title art (Each line is exactly 37 characters long)
TITLE_ART = [
    "╔══════════════════════════════╗",
    "║    ▄▄▄   ▄▄▄  ▄   ▄   ▄▄     ║",
    "║    █  █   █   █▀▄ █  █  █    ║",
    "║    █  █   █   █  ██  █  █    ║",
    "║    ▀▀▀   ▀▀▀  ▀   ▀   ▀▀     ║",
    "║          R  U  N  !          ║",
    "╚══════════════════════════════╝",
]

# === HIGH SCORE ===
SAVE_FILE = os.path.expanduser("~/.dino_highscore.json")

def load_high_score():
    try:
        with open(SAVE_FILE) as f:
            return json.load(f).get("high_score", 0)
    except Exception:
        return 0

def save_high_score(hs):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({"high_score": hs}, f)
    except Exception:
        pass

# === DRAW HELPERS ===

def draw_sprite(win, y, x, sprite, max_y, max_x, attr=0):
    for i, line in enumerate(sprite):
        py = y + i
        if 0 <= py < max_y:
            for j, ch in enumerate(line):
                px = x + j
                if 0 < px < max_x - 1 and ch != ' ':
                    try:
                        win.addstr(py, px, ch, attr)
                    except curses.error:
                        pass

def draw_centered(win, y, text, max_x, attr=0):
    x = max(0, max_x // 2 - len(text) // 2)
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass

def draw_solid_box(win, y, x, h, w, attr=0):
    for i in range(h):
        py = y + i
        try:
            win.addstr(py, x, " " * w, attr)
        except curses.error:
            pass

# === MAIN GAME ===

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    curses.start_color()
    curses.use_default_colors()

    # Day colors
    curses.init_pair(1, curses.COLOR_GREEN, -1)     # ground / cacti
    curses.init_pair(2, curses.COLOR_YELLOW, -1)    # score / UI / sun
    curses.init_pair(3, curses.COLOR_RED, -1)       # game over / particles
    curses.init_pair(4, curses.COLOR_CYAN, -1)      # clouds / info
    curses.init_pair(5, curses.COLOR_WHITE, -1)     # dino
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)   # milestone flash / combo / bird
    curses.init_pair(7, curses.COLOR_BLUE, -1)      # mountains
    # Night colors (8+)
    curses.init_pair(8, curses.COLOR_GREEN, -1)     # ground night
    curses.init_pair(9, curses.COLOR_YELLOW, -1)    # stars / night sun/moon
    curses.init_pair(10, curses.COLOR_WHITE, -1)    # moon / stars
    curses.init_pair(11, curses.COLOR_YELLOW, -1)   # coins / gold particles
    curses.init_pair(12, curses.COLOR_CYAN, -1)     # shield active / bubble

    max_y, max_x = stdscr.getmaxyx()

    ground_y = max_y - 4
    dino_x = 8
    dino_base_y = ground_y - len(DINO_RUN1)

    high_score = load_high_score()

    # Game state
    class State:
        jumping = False
        jump_vel = 0.0
        dino_y = float(dino_base_y)
        obstacles = []
        clouds = []
        stars = []
        mountains = []
        spawn_timer = 0
        spawn_interval = 40
        speed = 1.0
        score = 0
        game_over = False
        started = False
        paused = False
        frame = 0
        ground_offset = 0.0
        milestone_flash = 0
        last_milestone = 0
        is_night = False
        night_timer = 0
        new_high = False
        shake_frames = 0
        particles = []
        
        # Power-ups, Coins, Combos, and Double Jump State
        double_jumped = False
        coins = []
        coin_spawn_timer = 0
        coins_collected = 0
        powerups = []
        powerup_spawn_timer = 0
        shield_active = False
        shield_timer = 0
        shield_hits = 0
        magnet_active = False
        magnet_timer = 0
        near_misses = 0
        combo = 0
        combo_timer = 0
        combo_texts = []  # floating text for combos/bonuses
        slow_active = False
        slow_timer = 0
        slow_factor = 1.0

    s = State()

    # CONSTANTS
    JUMP_STRENGTH = -2.5
    DOUBLE_JUMP_STRENGTH = -2.1
    GRAVITY = 0.19
    MAX_SPEED = 4.0
    DAY_LENGTH = 1200      # frames per day/night cycle
    SHIELD_DURATION = 350  # frames (~10 seconds)
    MAGNET_DURATION = 400  # frames (~11.5 seconds)
    MAGNET_RANGE = 18      # attraction radius in characters
    SLOW_DURATION = 250    # frames (~7 seconds)

    def init_scenery():
        s.clouds = []
        for _ in range(3):
            s.clouds.append({
                "x": random.randint(0, max_x),
                "y": random.randint(2, ground_y // 3),
                "speed": random.uniform(0.1, 0.3),
            })
        s.stars = []
        for _ in range(25):
            s.stars.append({
                "x": random.randint(1, max_x - 2),
                "y": random.randint(1, ground_y // 2),
                "ch": random.choice(STAR_CHARS),
                "blink": random.randint(0, 30),
            })
        s.mountains = []
        mtn_x = random.randint(max_x // 4, max_x // 2)
        s.mountains.append({"x": mtn_x})
        s.mountains.append({"x": mtn_x + max_x // 2 + random.randint(-10, 10)})

    def reset():
        nonlocal high_score
        s.jumping = False
        s.jump_vel = 0.0
        s.dino_y = float(dino_base_y)
        s.obstacles = []
        s.spawn_timer = 0
        s.spawn_interval = 40
        s.speed = 1.0
        s.score = 0
        s.game_over = False
        s.started = False
        s.paused = False
        s.frame = 0
        s.ground_offset = 0.0
        s.milestone_flash = 0
        s.last_milestone = 0
        s.new_high = False
        s.shake_frames = 0
        s.particles = []
        
        # Reset new features
        s.double_jumped = False
        s.coins = []
        s.coin_spawn_timer = 0
        s.coins_collected = 0
        s.powerups = []
        s.powerup_spawn_timer = 0
        s.shield_active = False
        s.shield_timer = 0
        s.shield_hits = 0
        s.magnet_active = False
        s.magnet_timer = 0
        s.near_misses = 0
        s.combo = 0
        s.combo_timer = 0
        s.combo_texts = []
        s.slow_active = False
        s.slow_timer = 0
        s.slow_factor = 1.0
        init_scenery()

    def spawn_particles(x, y, count=6, color=None, chars=None):
        if color is None:
            color = curses.color_pair(3) | curses.A_BOLD
        if chars is None:
            chars = ["*", "x", "#", "!", "~", "+", "·"]
        for _ in range(count):
            s.particles.append({
                "x": float(x + random.uniform(-1.5, 1.5)),
                "y": float(y + random.uniform(-1.0, 1.0)),
                "vx": random.uniform(-1.8, 1.8),
                "vy": random.uniform(-2.2, -0.4),
                "life": random.randint(6, 18),
                "ch": random.choice(chars),
                "color": color
            })

    def check_collision(r1, r2):
        y1, x1, h1, w1 = r1
        y2, x2, h2, w2 = r2
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    init_scenery()

    # === GAME LOOP ===
    while True:
        loop_start = time.monotonic()

        # --- Input ---
        pressed = set()
        while True:
            k = stdscr.getch()
            if k == -1:
                break
            pressed.add(k)

        # Quit
        if 27 in pressed or ord('q') in pressed or ord('Q') in pressed:
            break

        # Pause
        if ord('p') in pressed or ord('P') in pressed:
            if s.started and not s.game_over:
                s.paused = not s.paused

        # Handle screen resizing dynamically
        if curses.KEY_RESIZE in pressed:
            curses.update_lines_cols()
            max_y, max_x = stdscr.getmaxyx()
            ground_y = max_y - 4
            dino_base_y = ground_y - len(DINO_RUN1)
            # Re-align Dino if it's sitting on the ground
            if not s.jumping:
                s.dino_y = float(dino_base_y)

        # Game states input handlers
        if s.game_over:
            if (ord(' ') in pressed or 10 in pressed or 13 in pressed or 
                curses.KEY_ENTER in pressed or curses.KEY_UP in pressed or 
                ord('w') in pressed or ord('W') in pressed):
                reset()
                continue
        elif not s.paused:
            # Enter key to start the game without jumping if not started yet
            if not s.started:
                if 10 in pressed or 13 in pressed or curses.KEY_ENTER in pressed:
                    s.started = True

            # Jump / Double-Jump input trigger
            if ord(' ') in pressed or curses.KEY_UP in pressed or ord('w') in pressed or ord('W') in pressed:
                if not s.jumping:
                    s.jumping = True
                    s.started = True
                    s.jump_vel = JUMP_STRENGTH
                    s.double_jumped = False
                    # Spawn jump ground puff particles
                    spawn_particles(dino_x + 3, ground_y - 1, count=5, 
                                    color=curses.color_pair(4) | curses.A_DIM, chars=[".", "~", "o"])
                elif not s.double_jumped:
                    # Double jump in mid-air!
                    s.jump_vel = DOUBLE_JUMP_STRENGTH
                    s.double_jumped = True
                    # Double-jump particle splash underneath the Dino!
                    spawn_particles(dino_x + 4, s.dino_y + len(DINO_RUN1) - 1, count=8,
                                    color=curses.color_pair(12) | curses.A_BOLD, chars=["*", "x", "+", "·"])
                    # Floating text pop up
                    s.combo_texts.append({
                        "text": "DOUBLE JUMP!",
                        "x": float(dino_x),
                        "y": s.dino_y - 1,
                        "vy": -0.3,
                        "life": 25,
                        "color": curses.color_pair(12) | curses.A_BOLD
                    })

        # --- Update Game Logic & Frame Animation ---
        # Critical: Only increment the frame animation ticks when NOT paused
        if not s.paused:
            s.frame += 1

        if s.started and not s.game_over and not s.paused and not (max_y < 22 or max_x < 60):
            # Physics / Gravity updates
            if s.jumping:
                s.jump_vel += GRAVITY
                s.dino_y += s.jump_vel
                if s.dino_y >= float(dino_base_y):
                    s.dino_y = float(dino_base_y)
                    s.jumping = False
                    s.double_jumped = False
                    s.jump_vel = 0.0

            # Day/night cycle update
            s.night_timer = (s.night_timer + 1) % DAY_LENGTH
            s.is_night = s.night_timer > DAY_LENGTH // 2

            # Obstacles Spawner (Supporting small, large, cluster, tall, wavy, blossom)
            s.spawn_timer += 1
            if s.spawn_timer >= s.spawn_interval:
                s.spawn_timer = 0
                min_gap = max(20, int(40 - s.speed * 3.5))
                max_gap = max(30, int(60 - s.speed * 3.5))
                s.spawn_interval = random.randint(min_gap, max_gap)

                r = random.random()
                if s.speed < 1.6:
                    if r < 0.4:
                        s.obstacles.append({"type": "cactus_small", "x": float(max_x + 2)})
                    elif r < 0.65:
                        s.obstacles.append({"type": "cactus_large", "x": float(max_x + 2)})
                    elif r < 0.85:
                        s.obstacles.append({"type": "cactus_wavy", "x": float(max_x + 2)})
                    else:
                        s.obstacles.append({"type": "cactus_blossom", "x": float(max_x + 2)})
                elif s.speed < 2.6:
                    if r < 0.2:
                        s.obstacles.append({"type": "cactus_small", "x": float(max_x + 2)})
                    elif r < 0.35:
                        s.obstacles.append({"type": "cactus_large", "x": float(max_x + 2)})
                    elif r < 0.5:
                        s.obstacles.append({"type": "cactus_cluster", "x": float(max_x + 2)})
                    elif r < 0.62:
                        s.obstacles.append({"type": "cactus_tall", "x": float(max_x + 2)})
                    elif r < 0.74:
                        s.obstacles.append({"type": "cactus_wavy", "x": float(max_x + 2)})
                    elif r < 0.85:
                        s.obstacles.append({"type": "cactus_blossom", "x": float(max_x + 2)})
                    else:
                        bird_heights = [ground_y - 4, ground_y - 6, ground_y - 8]
                        s.obstacles.append({"type": "bird", "x": float(max_x + 2),
                                            "y": random.choice(bird_heights)})
                else:
                    if r < 0.12:
                        s.obstacles.append({"type": "cactus_small", "x": float(max_x + 2)})
                    elif r < 0.24:
                        s.obstacles.append({"type": "cactus_large", "x": float(max_x + 2)})
                    elif r < 0.35:
                        s.obstacles.append({"type": "cactus_cluster", "x": float(max_x + 2)})
                    elif r < 0.45:
                        s.obstacles.append({"type": "cactus_tall", "x": float(max_x + 2)})
                    elif r < 0.55:
                        s.obstacles.append({"type": "cactus_wavy", "x": float(max_x + 2)})
                    elif r < 0.65:
                        s.obstacles.append({"type": "cactus_blossom", "x": float(max_x + 2)})
                    else:
                        bird_heights = [ground_y - 4, ground_y - 6, ground_y - 9]
                        s.obstacles.append({"type": "bird", "x": float(max_x + 2),
                                            "y": random.choice(bird_heights)})

            # Move Obstacles
            for obs in s.obstacles:
                obs["x"] -= s.speed
            s.obstacles = [o for o in s.obstacles if o["x"] > -15]

            # Spawning Coins
            s.coin_spawn_timer += 1
            if s.coin_spawn_timer >= random.randint(35, 75):
                s.coin_spawn_timer = 0
                coin_y_choices = [ground_y - 3, ground_y - 6, ground_y - 9]
                s.coins.append({
                    "x": float(max_x + 2),
                    "y": float(random.choice(coin_y_choices))
                })

            # Spawning Power-ups
            s.powerup_spawn_timer += 1
            if s.powerup_spawn_timer >= random.randint(320, 580):
                s.powerup_spawn_timer = 0
                pup_type = "shield" if random.random() < 0.5 else "magnet"
                s.powerups.append({
                    "type": pup_type,
                    "x": float(max_x + 2),
                    "y": float(ground_y - 5)
                })

            # Move Coins (Handle Magnet Pull Vector Physics!)
            dino_center_y = s.dino_y + len(DINO_RUN1) // 2
            dino_center_x = dino_x + len(DINO_RUN1[0]) // 2 if isinstance(DINO_RUN1, list) else dino_x + 6

            for coin in s.coins:
                if s.magnet_active:
                    dx_vec = dino_center_x - coin["x"]
                    dy_vec = dino_center_y - coin["y"]
                    dist = (dx_vec**2 + dy_vec**2)**0.5
                    if dist < MAGNET_RANGE:
                        # Pull coin dynamically towards Dino
                        pull_speed = s.speed * 1.4
                        coin["x"] += (dx_vec / dist) * pull_speed
                        coin["y"] += (dy_vec / dist) * pull_speed
                    else:
                        coin["x"] -= s.speed
                else:
                    coin["x"] -= s.speed
            s.coins = [c for c in s.coins if c["x"] > -5]

            # Move Power-ups
            for pup in s.powerups:
                pup["x"] -= s.speed
            s.powerups = [p for p in s.powerups if p["x"] > -5]

            # Decaying Timers (Power-ups & Combos)
            if s.shield_active:
                s.shield_timer -= 1
                if s.shield_timer <= 0:
                    s.shield_active = False
                    s.combo_texts.append({
                        "text": "SHIELD EXPIRED",
                        "x": float(dino_x),
                        "y": s.dino_y - 1,
                        "vy": -0.3,
                        "life": 30,
                        "color": curses.color_pair(12) | curses.A_DIM
                    })

            if s.magnet_active:
                s.magnet_timer -= 1
                if s.magnet_timer <= 0:
                    s.magnet_active = False
                    s.combo_texts.append({
                        "text": "MAGNET EXPIRED",
                        "x": float(dino_x),
                        "y": s.dino_y - 1,
                        "vy": -0.3,
                        "life": 30,
                        "color": curses.color_pair(11) | curses.A_DIM
                    })

            if s.combo > 0:
                s.combo_timer -= 1
                if s.combo_timer <= 0:
                    s.combo = 0

            # Move Scenery (Background Cloud / Mountain parallax)
            for c in s.clouds:
                c["x"] -= c["speed"] * (s.speed * 0.3)
                if c["x"] < -len(CLOUD[0]):
                    c["x"] = float(max_x + random.randint(5, 30))
                    c["y"] = random.randint(2, ground_y // 3)

            for m in s.mountains:
                m["x"] -= s.speed * 0.08
                if m["x"] < -len(MOUNTAIN[0]):
                    m["x"] = float(max_x + random.randint(10, 40))

            # Incremental Score
            if s.frame % 3 == 0:
                s.score += 1

            # Milestone Flashing (Every 100 points)
            if s.score // 100 > s.last_milestone:
                s.last_milestone = s.score // 100
                s.milestone_flash = 30
                try:
                    curses.beep()
                except curses.error:
                    pass

            if s.milestone_flash > 0:
                s.milestone_flash -= 1

            # Speed Progression
            if s.frame % 180 == 0:
                s.speed = min(s.speed + 0.1, MAX_SPEED)

            s.ground_offset = (s.ground_offset + s.speed) % 6

            # Particle Physics Update
            for p in s.particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.15  # gravity effect on particles
                p["life"] -= 1
            s.particles = [p for p in s.particles if p["life"] > 0]

            # Floating Text Physics Update
            for txt in s.combo_texts:
                txt["x"] += txt.get("vx", 0.0)
                txt["y"] += txt.get("vy", -0.2)
                txt["life"] -= 1
            s.combo_texts = [t for t in s.combo_texts if t["life"] > 0]

            # --- Collision Rects Calculations (Ducking Sprites Removed!) ---
            cur_y = int(s.dino_y)
            cur_sprite = DINO_RUN1 if not s.jumping else DINO_JUMP_SPRITE

            # Tighter dino hitbox (shrink padding)
            dh = len(cur_sprite) - 2
            dw = len(cur_sprite[0]) - 4
            dino_rect = (cur_y + 1, dino_x + 2, dh, dw)

            # Check Coins Collisions
            remaining_coins = []
            for coin in s.coins:
                coin_rect = (int(coin["y"]), int(coin["x"]), 3, 3)
                if check_collision(dino_rect, coin_rect):
                    s.coins_collected += 1
                    coin_val = 15 + (5 * s.combo)
                    s.score += coin_val
                    # Spawn sparkling golden particles
                    spawn_particles(coin["x"] + 1, coin["y"] + 1, count=6,
                                    color=curses.color_pair(11) | curses.A_BOLD, chars=["*", "+", "·"])
                    # Floating text pop up
                    s.combo_texts.append({
                        "text": f"+{coin_val} PTS!",
                        "x": coin["x"],
                        "y": coin["y"] - 1,
                        "vy": -0.4,
                        "life": 30,
                        "color": curses.color_pair(11) | curses.A_BOLD
                    })
                else:
                    remaining_coins.append(coin)
            s.coins = remaining_coins

            # Check Power-ups Collisions
            remaining_pups = []
            for pup in s.powerups:
                pup_rect = (int(pup["y"]), int(pup["x"]), 3, 3)
                if check_collision(dino_rect, pup_rect):
                    if pup["type"] == "shield":
                        s.shield_active = True
                        s.shield_timer = SHIELD_DURATION
                        # Spawn glowing cyan particles
                        spawn_particles(pup["x"] + 1, pup["y"] + 1, count=12,
                                        color=curses.color_pair(12) | curses.A_BOLD, chars=["◇", "*", "+"])
                        s.combo_texts.append({
                            "text": "⚡ SHIELD ACQUIRED!",
                            "x": float(dino_x),
                            "y": s.dino_y - 2,
                            "vy": -0.3,
                            "life": 40,
                            "color": curses.color_pair(12) | curses.A_BOLD
                        })
                    elif pup["type"] == "magnet":
                        s.magnet_active = True
                        s.magnet_timer = MAGNET_DURATION
                        # Spawn glowing magenta particles
                        spawn_particles(pup["x"] + 1, pup["y"] + 1, count=12,
                                        color=curses.color_pair(6) | curses.A_BOLD, chars=["M", "*", "+"])
                        s.combo_texts.append({
                            "text": "🧲 MAGNET ACQUIRED!",
                            "x": float(dino_x),
                            "y": s.dino_y - 2,
                            "vy": -0.3,
                            "life": 40,
                            "color": curses.color_pair(6) | curses.A_BOLD
                        })
                    try:
                        curses.beep()
                        curses.flash()
                    except curses.error:
                        pass
                else:
                    remaining_pups.append(pup)
            s.powerups = remaining_pups

            # Check Obstacles Collisions & Near Misses (Expanded for all Cactus variants)
            remaining_obstacles = []
            for obs in s.obstacles:
                ox = int(obs["x"])
                if obs["type"] == "cactus_small":
                    sprite = CACTUS_SMALL
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                elif obs["type"] == "cactus_large":
                    sprite = CACTUS_LARGE
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                elif obs["type"] == "cactus_cluster":
                    sprite = CACTUS_CLUSTER
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                elif obs["type"] == "cactus_tall":
                    sprite = CACTUS_TALL
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                elif obs["type"] == "cactus_wavy":
                    sprite = CACTUS_WAVY
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                elif obs["type"] == "cactus_blossom":
                    sprite = CACTUS_BLOSSOM
                    oy = ground_y - len(sprite)
                    obs_rect = (oy + 1, ox + 1, len(sprite) - 1, len(sprite[0]) - 2)
                else:  # Bird
                    oy = obs["y"]
                    sprite = BIRD_UP
                    obs_rect = (oy, ox + 1, len(sprite), len(sprite[0]) - 2)

                # 1. Collision detection
                if check_collision(dino_rect, obs_rect):
                    if s.shield_active:
                        # Shield absorbs the collision!
                        s.shield_active = False
                        s.shield_timer = 0
                        s.shake_frames = 12
                        # Spawn magnificent fiery explosion particles!
                        spawn_particles(ox + len(sprite[0]) // 2, oy + len(sprite) // 2, count=18,
                                        color=curses.color_pair(12) | curses.A_BOLD, chars=["#", "%", "*", "@"])
                        s.combo_texts.append({
                            "text": "💥 SHIELD DEFLECTED!",
                            "x": float(dino_x),
                            "y": s.dino_y - 2,
                            "vy": -0.4,
                            "life": 45,
                            "color": curses.color_pair(12) | curses.A_BOLD
                        })
                        try:
                            curses.beep()
                            curses.flash()
                        except curses.error:
                            pass
                        # Destroy obstacle (do not append to remaining_obstacles)
                        continue
                    else:
                        # Standard game over collision
                        s.game_over = True
                        s.shake_frames = 12
                        spawn_particles(dino_x + 4, cur_y + 3, count=15, 
                                        color=curses.color_pair(3) | curses.A_BOLD)
                        try:
                            curses.flash()
                            curses.beep()
                        except curses.error:
                            pass
                        if s.score > high_score:
                            high_score = s.score
                            s.new_high = True
                            save_high_score(high_score)
                
                # 2. Near Miss detection
                elif not obs.get("near_missed", False):
                    # Horizontal overlap check: obstacle has reached Dino's column
                    if dino_x - 2 <= ox <= dino_x + 5:
                        # Dino is safely above this obstacle (ducking checks removed)
                        obs["near_missed"] = True
                        s.near_misses += 1
                        s.combo += 1
                        s.combo_timer = 120  # ~3.5 seconds
                        near_bonus = 50 * s.combo
                        s.score += near_bonus
                        # Spawn flashy sparks
                        spawn_particles(ox + len(sprite[0]) // 2, oy, count=5,
                                        color=curses.color_pair(6) | curses.A_BOLD, chars=["+", "*", "·"])
                        s.combo_texts.append({
                            "text": f"NEAR MISS! x{s.combo} (+{near_bonus} PTS)",
                            "x": float(dino_x),
                            "y": s.dino_y - 1.5,
                            "vy": -0.35,
                            "life": 35,
                            "color": curses.color_pair(6) | curses.A_BOLD
                        })

                remaining_obstacles.append(obs)
            s.obstacles = remaining_obstacles

        # --- Screen Shake Logic ---
        shake_y = 0
        shake_x = 0
        if s.shake_frames > 0:
            s.shake_frames -= 1
            shake_y = random.choice([-1, 0, 1])
            shake_x = random.choice([-1, 0, 1])

        # --- Draw Render Screen ---
        stdscr.erase()

        gy = ground_y + shake_y
        sx = shake_x

        # Fallback render screen check (Graceful dynamic resizing UI message)
        if max_y < 22 or max_x < 60:
            draw_centered(stdscr, max_y // 2 - 1, "┌─────────────────────────────────────┐", max_x, curses.color_pair(3))
            draw_centered(stdscr, max_y // 2,     "│  ⚠️  TERMINAL WINDOW TOO SMALL!      │", max_x, curses.color_pair(3) | curses.A_BOLD)
            draw_centered(stdscr, max_y // 2 + 1, "│  Please expand to at least 60x22    │", max_x, curses.color_pair(5))
            draw_centered(stdscr, max_y // 2 + 2, "└─────────────────────────────────────┘", max_x, curses.color_pair(3))
            stdscr.refresh()
            # Loop delay
            elapsed = time.monotonic() - loop_start
            time.sleep(max(0, 0.028 - elapsed))
            continue

        # Stars in Night Sky (Twinkle Effect - Paused when game is paused)
        if s.is_night:
            for star in s.stars:
                if (s.frame + star["blink"]) % 40 < 30:
                    try:
                        stdscr.addstr(star["y"], star["x"], star["ch"],
                                      curses.color_pair(9) | curses.A_DIM)
                    except curses.error:
                        pass

        # Sliding Celestial Objects (Sun & Moon slide smoothly across the sky)
        if not s.is_night:
            progress = s.night_timer / (DAY_LENGTH // 2)
            sun_x = int(max_x - progress * (max_x + 15))
            draw_sprite(stdscr, 2 + shake_y, sun_x + sx, SUN, max_y, max_x, curses.color_pair(2) | curses.A_BOLD)
        else:
            progress = (s.night_timer - DAY_LENGTH // 2) / (DAY_LENGTH // 2)
            moon_x = int(max_x - progress * (max_x + 15))
            draw_sprite(stdscr, 2 + shake_y, moon_x + sx, MOON, max_y, max_x, curses.color_pair(10) | curses.A_BOLD)

        # Mountains (Background Parallax scrolling)
        mtn_attr = curses.color_pair(7) | curses.A_DIM
        for m in s.mountains:
            mx = int(m["x"]) + sx
            mtn_y = gy - len(MOUNTAIN)
            draw_sprite(stdscr, mtn_y, mx, MOUNTAIN, max_y, max_x, mtn_attr)

        # Clouds
        cloud_attr = curses.color_pair(4) | curses.A_DIM
        for c in s.clouds:
            cx = int(c["x"]) + sx
            draw_sprite(stdscr, int(c["y"]) + shake_y, cx, CLOUD, max_y, max_x, cloud_attr)

        # Ground texture scrolling
        ground_line = ""
        for i in range(max_x - 1):
            gi = i + int(s.ground_offset)
            if gi % 12 == 0:
                ground_line += "^"
            elif gi % 6 == 0:
                ground_line += "~"
            elif gi % 4 == 0:
                ground_line += "."
            else:
                ground_line += "▁"
        ground_attr = curses.color_pair(1)
        try:
            stdscr.addstr(gy, 0, ground_line[:max_x - 1], ground_attr)
        except curses.error:
            pass

        # Sub-ground sub-scrolling texture
        sub_ground = ""
        for i in range(max_x - 1):
            gi = i + int(s.ground_offset * 0.5)
            if gi % 8 == 0:
                sub_ground += "░"
            elif gi % 5 == 0:
                sub_ground += "▒"
            else:
                sub_ground += " "
        try:
            stdscr.addstr(gy + 1, 0, sub_ground[:max_x - 1], curses.color_pair(1) | curses.A_DIM)
        except curses.error:
            pass

        # Draw Obstacles (Supporting all new Cactus designs)
        for obs in s.obstacles:
            ox = int(obs["x"]) + sx
            if obs["type"] == "cactus_small":
                draw_sprite(stdscr, gy - len(CACTUS_SMALL), ox, CACTUS_SMALL,
                            max_y, max_x, curses.color_pair(1))
            elif obs["type"] == "cactus_large":
                draw_sprite(stdscr, gy - len(CACTUS_LARGE), ox, CACTUS_LARGE,
                            max_y, max_x, curses.color_pair(1))
            elif obs["type"] == "cactus_cluster":
                draw_sprite(stdscr, gy - len(CACTUS_CLUSTER), ox, CACTUS_CLUSTER,
                            max_y, max_x, curses.color_pair(1))
            elif obs["type"] == "cactus_tall":
                draw_sprite(stdscr, gy - len(CACTUS_TALL), ox, CACTUS_TALL,
                            max_y, max_x, curses.color_pair(1))
            elif obs["type"] == "cactus_wavy":
                draw_sprite(stdscr, gy - len(CACTUS_WAVY), ox, CACTUS_WAVY,
                            max_y, max_x, curses.color_pair(1))
            elif obs["type"] == "cactus_blossom":
                draw_sprite(stdscr, gy - len(CACTUS_BLOSSOM), ox, CACTUS_BLOSSOM,
                            max_y, max_x, curses.color_pair(1))
            else:  # Bird
                bird_sprite = BIRD_UP if s.frame % 14 < 7 else BIRD_DOWN
                draw_sprite(stdscr, obs["y"] + shake_y, ox, bird_sprite,
                            max_y, max_x, curses.color_pair(6))

        # Draw Coins
        for coin in s.coins:
            draw_sprite(stdscr, int(coin["y"]) + shake_y, int(coin["x"]) + sx, COIN,
                        max_y, max_x, curses.color_pair(11) | curses.A_BOLD)

        # Draw Power-ups
        for pup in s.powerups:
            pup_sprite = SHIELD_ICON if pup["type"] == "shield" else MAGNET_ICON
            pup_color = curses.color_pair(12) if pup["type"] == "shield" else curses.color_pair(6)
            draw_sprite(stdscr, int(pup["y"]) + shake_y, int(pup["x"]) + sx, pup_sprite,
                        max_y, max_x, pup_color | curses.A_BOLD)

        # Draw Dino (ducking animation frames fully removed!)
        if s.game_over:
            dino_sprite = DINO_DEAD
            dy = int(s.dino_y) + shake_y
        elif s.jumping:
            dino_sprite = DINO_JUMP_SPRITE
            dy = int(s.dino_y) + shake_y
        else:
            # Toggles foot animation based on s.frame, which freezes when game is paused
            dino_sprite = DINO_RUN1 if s.frame % 8 < 4 else DINO_RUN2
            dy = int(s.dino_y) + shake_y

        dino_attr = curses.color_pair(5) | curses.A_BOLD
        draw_sprite(stdscr, dy, dino_x + sx, dino_sprite, max_y, max_x, dino_attr)

        # --- Draw Dino Power-up Auric Overlay Effects ---
        # 1. Shield active glowing cyan barrier bubble surrounding Dino
        if s.shield_active:
            shield_color = curses.color_pair(12) | curses.A_BOLD
            if s.shield_timer > 60 or s.frame % 6 < 3:
                for idx_y in range(len(dino_sprite)):
                    py = dy + idx_y
                    if 0 <= py < max_y:
                        try:
                            stdscr.addstr(py, dino_x + sx - 1, "█", shield_color)
                            stdscr.addstr(py, dino_x + sx + len(dino_sprite[0]), "█", shield_color)
                        except curses.error:
                            pass
        
        # 2. Magnet active glowing wave pulses around Dino
        if s.magnet_active:
            magnet_color = curses.color_pair(11) | curses.A_BOLD
            if s.magnet_timer > 60 or s.frame % 6 < 3:
                wave_char_left = "«" if s.frame % 10 < 5 else "<"
                wave_char_right = "»" if s.frame % 10 < 5 else ">"
                try:
                    stdscr.addstr(dy + 3, dino_x + sx - 3, wave_char_left, magnet_color)
                    stdscr.addstr(dy + 3, dino_x + sx + len(dino_sprite[0]) + 2, wave_char_right, magnet_color)
                except curses.error:
                    pass

        # Draw Particles
        for p in s.particles:
            px, py = int(p["x"]) + sx, int(p["y"]) + shake_y
            if 0 < px < max_x - 1 and 0 <= py < max_y:
                try:
                    stdscr.addstr(py, px, p["ch"], p["color"])
                except curses.error:
                    pass

        # Draw Floating Arcade Text popups
        for txt in s.combo_texts:
            tx, ty = int(txt["x"]), int(txt["y"])
            if 0 < tx < max_x - 1 and 0 <= ty < max_y:
                try:
                    stdscr.addstr(ty, tx, txt["text"], txt["color"])
                except curses.error:
                    pass

        # --- HUD RENDERING PANEL ---
        if s.milestone_flash > 0 and s.milestone_flash % 4 < 2:
            score_attr = curses.color_pair(6) | curses.A_BOLD
        else:
            score_attr = curses.color_pair(2) | curses.A_BOLD

        score_str = f" {s.score:05d} "
        hi_str = f" HI {high_score:05d} "
        try:
            stdscr.addstr(1, max_x - len(score_str) - len(hi_str) - 3, hi_str,
                          curses.color_pair(4))
            stdscr.addstr(1, max_x - len(score_str) - 2, score_str, score_attr)
        except curses.error:
            pass

        # Speed progression meter
        speed_bar = "▪" * int(s.speed * 3)
        try:
            stdscr.addstr(2, max_x - len(speed_bar) - 8, f"SPD {speed_bar}", curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass

        # Day/Night phase indicator
        indicator = "☾ NIGHT" if s.is_night else "☀ DAY"
        try:
            stdscr.addstr(1, 2, indicator, curses.color_pair(9 if s.is_night else 2) | curses.A_BOLD)
        except curses.error:
            pass

        # Coins collected HUD icon
        coins_str = f"◉ {s.coins_collected:03d} COINS"
        try:
            stdscr.addstr(2, 2, coins_str, curses.color_pair(11) | curses.A_BOLD)
        except curses.error:
            pass

        # Multi-stacked Active Status Meters (Shield / Magnet / Slow-mo / Combo meters)
        hud_row = 3
        if s.shield_active:
            bar_len = int((s.shield_timer / SHIELD_DURATION) * 10)
            bar_str = "█" * bar_len + "░" * (10 - bar_len)
            try:
                stdscr.addstr(hud_row, 2, f"🛡️ SHIELD [{bar_str}] {s.shield_timer:03d}",
                              curses.color_pair(12) | curses.A_BOLD)
                hud_row += 1
            except curses.error:
                pass

        if s.magnet_active:
            bar_len = int((s.magnet_timer / MAGNET_DURATION) * 10)
            bar_str = "█" * bar_len + "░" * (10 - bar_len)
            try:
                stdscr.addstr(hud_row, 2, f"🧲 MAGNET [{bar_str}] {s.magnet_timer:03d}",
                              curses.color_pair(11) | curses.A_BOLD)
                hud_row += 1
            except curses.error:
                pass

        if s.slow_active:
            bar_len = int((s.slow_timer / SLOW_DURATION) * 10)
            bar_str = "█" * bar_len + "░" * (10 - bar_len)
            try:
                stdscr.addstr(hud_row, 2, f"⏳ SLOW-MO [{bar_str}] {s.slow_timer:03d}",
                              curses.color_pair(6) | curses.A_BOLD)
                hud_row += 1
            except curses.error:
                pass

        if s.combo > 0:
            bar_len = int((s.combo_timer / 120) * 10)
            bar_str = "█" * bar_len + "░" * (10 - bar_len)
            try:
                stdscr.addstr(hud_row, 2, f"⚡ COMBO x{s.combo} [{bar_str}]",
                              curses.color_pair(6) | curses.A_BOLD)
                hud_row += 1
            except curses.error:
                pass

        # Start Screen Title Overlay (Duck Controls Removed!)
        if not s.started and not s.game_over:
            ty = max_y // 2 - 8
            # Draw a solid opaque box to wipe backgrounds behind the title screen card
            card_w = 66
            card_x = max(0, max_x // 2 - card_w // 2)
            draw_solid_box(stdscr, ty - 1, card_x, 18, card_w, 0)

            for i, line in enumerate(TITLE_ART):
                draw_centered(stdscr, ty + i, line, max_x, curses.color_pair(2) | curses.A_BOLD)

            draw_centered(stdscr, ty + len(TITLE_ART) + 1,
                          "[ SPACE / ↑ / W ] Jump / Double-Jump      [ P ] Pause", max_x, curses.color_pair(5))
            draw_centered(stdscr, ty + len(TITLE_ART) + 2,
                          "[ Q / ESC ] Quit Game", max_x, curses.color_pair(5))

            draw_centered(stdscr, ty + len(TITLE_ART) + 4,
                          "--- ARCADE FEATURES ---", max_x, curses.color_pair(6) | curses.A_BOLD)
            draw_centered(stdscr, ty + len(TITLE_ART) + 5,
                          "○ Coins (+15 Pts)   |   ◇ Shields (Barrier Blocks Obstacle)", max_x, curses.color_pair(4))
            draw_centered(stdscr, ty + len(TITLE_ART) + 6,
                          "╔M╗ Magnet (Attracts Coins)  |  ⏳ Slow-mo (Matrix Spacetime Warp)", max_x, curses.color_pair(4))

            if s.frame % 40 < 28:
                draw_centered(stdscr, ty + len(TITLE_ART) + 8,
                              ">>> Press SPACE to start <<<", max_x,
                              curses.color_pair(6) | curses.A_BOLD)

        # Pause Menu Overlay (Optimized, mathematically aligned, and opaque-backed)
        if s.paused:
            card_x = max(0, max_x // 2 - 11)
            draw_solid_box(stdscr, max_y // 2 - 2, card_x, 5, 22, 0)

            draw_centered(stdscr, max_y // 2 - 1,
                          "┌──────────────────┐", max_x, curses.color_pair(2))
            draw_centered(stdscr, max_y // 2,
                          "│     || PAUSED     │", max_x, curses.color_pair(2) | curses.A_BOLD)
            draw_centered(stdscr, max_y // 2 + 1,
                          "└──────────────────┘", max_x, curses.color_pair(2))

        # Game Over Overlay (Solid color borders, dynamic scorecard, opaque background card)
        if s.game_over:
            cy = max_y // 2 - 4
            box_x = max(0, max_x // 2 - 14)
            card_x = max(0, max_x // 2 - 15)
            
            # 1. Draw a solid opaque box behind the card to wipe backgrounds
            draw_solid_box(stdscr, cy - 1, card_x, 9, 30, 0)

            # 2. Draw the border box outline in solid Red (color pair 3)
            box_color = curses.color_pair(3)
            draw_centered(stdscr, cy,     "┌──────────────────────────┐", max_x, box_color)
            draw_centered(stdscr, cy + 1, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 2, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 3, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 4, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 5, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 6, "└──────────────────────────┘", max_x, box_color)

            # 3. Draw the contents inside the border box using individual colors
            # The inside is 26 characters wide, starting at box_x + 1
            text_x = box_x + 1
            
            # Game Over text (Red / Bold)
            try:
                stdscr.addstr(cy + 1, text_x, "       GAME OVER!         ", curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass

            # Score text (Yellow)
            score_val_str = f"{s.score:05d}"
            try:
                stdscr.addstr(cy + 2, text_x, f"    Score:  {score_val_str:<14}", curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

            # Coins text (Gold)
            coins_val_str = f"{s.coins_collected:03d}"
            try:
                stdscr.addstr(cy + 3, text_x, f"    Coins:  {coins_val_str:<14}", curses.color_pair(11) | curses.A_BOLD)
            except curses.error:
                pass

            # High Score text (Magenta if new high, else Cyan)
            if s.new_high:
                try:
                    stdscr.addstr(cy + 4, text_x, "   * NEW HIGH SCORE *     ", curses.color_pair(6) | curses.A_BOLD)
                except curses.error:
                    pass
            else:
                best_val_str = f"{high_score:05d}"
                try:
                    stdscr.addstr(cy + 4, text_x, f"    Best:   {best_val_str:<14}", curses.color_pair(4) | curses.A_BOLD)
                except curses.error:
                    pass

            # Retry instruction (White)
            try:
                stdscr.addstr(cy + 5, text_x, "    Press SPACE to retry  ", curses.color_pair(5))
            except curses.error:
                pass

        stdscr.refresh()

        # Frame Rate timing stabilization (~35 FPS)
        elapsed = time.monotonic() - loop_start
        sleep_time = max(0, 0.028 - elapsed)
        time.sleep(sleep_time)

if __name__ == "__main__":
    curses.wrapper(main)
