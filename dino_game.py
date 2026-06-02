import curses
import random
import time
import os
import json
import struct
import math
import io
import wave
import subprocess
import tempfile
import atexit

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

# === THEMES ===
THEMES = {
    "classic": {
        "name": "Classic Arcade",
        "price": 0,
        "colors": [
            (1, curses.COLOR_GREEN, -1),     # ground / cacti
            (2, curses.COLOR_YELLOW, -1),    # score / UI / sun
            (3, curses.COLOR_RED, -1),       # game over / particles
            (4, curses.COLOR_CYAN, -1),      # clouds / info
            (5, curses.COLOR_WHITE, -1),     # dino
            (6, curses.COLOR_MAGENTA, -1),   # milestone / combo / bird
            (7, curses.COLOR_BLUE, -1),      # mountains
            (8, curses.COLOR_GREEN, -1),     # ground night
            (9, curses.COLOR_YELLOW, -1),    # stars / night sun/moon
            (10, curses.COLOR_WHITE, -1),    # moon / stars
            (11, curses.COLOR_YELLOW, -1),   # coins / gold particles
            (12, curses.COLOR_CYAN, -1),     # shield active / bubble
        ]
    },
    "matrix": {
        "name": "Matrix Overload",
        "price": 15,
        "colors": [
            (1, curses.COLOR_GREEN, -1),
            (2, curses.COLOR_GREEN, -1),
            (3, curses.COLOR_GREEN, -1),
            (4, curses.COLOR_GREEN, -1),
            (5, curses.COLOR_GREEN, -1),
            (6, curses.COLOR_RED, -1),
            (7, curses.COLOR_GREEN, -1),
            (8, curses.COLOR_GREEN, -1),
            (9, curses.COLOR_GREEN, -1),
            (10, curses.COLOR_GREEN, -1),
            (11, curses.COLOR_WHITE, -1),
            (12, curses.COLOR_CYAN, -1),
        ]
    },
    "sunset": {
        "name": "Sunset Ridge",
        "price": 30,
        "colors": [
            (1, curses.COLOR_RED, -1),
            (2, curses.COLOR_YELLOW, -1),
            (3, curses.COLOR_RED, -1),
            (4, curses.COLOR_YELLOW, -1),
            (5, curses.COLOR_WHITE, -1),
            (6, curses.COLOR_YELLOW, -1),
            (7, curses.COLOR_RED, -1),
            (8, curses.COLOR_RED, -1),
            (9, curses.COLOR_YELLOW, -1),
            (10, curses.COLOR_WHITE, -1),
            (11, curses.COLOR_YELLOW, -1),
            (12, curses.COLOR_RED, -1),
        ]
    },
    "cyberpunk": {
        "name": "Neon Cyberpunk",
        "price": 50,
        "colors": [
            (1, curses.COLOR_MAGENTA, -1),
            (2, curses.COLOR_CYAN, -1),
            (3, curses.COLOR_RED, -1),
            (4, curses.COLOR_BLUE, -1),
            (5, curses.COLOR_CYAN, -1),
            (6, curses.COLOR_MAGENTA, -1),
            (7, curses.COLOR_BLUE, -1),
            (8, curses.COLOR_MAGENTA, -1),
            (9, curses.COLOR_CYAN, -1),
            (10, curses.COLOR_CYAN, -1),
            (11, curses.COLOR_YELLOW, -1),
            (12, curses.COLOR_BLUE, -1),
        ]
    },
    "snow": {
        "name": "Ice & Snow",
        "price": 80,
        "colors": [
            (1, curses.COLOR_WHITE, -1),
            (2, curses.COLOR_CYAN, -1),
            (3, curses.COLOR_BLUE, -1),
            (4, curses.COLOR_CYAN, -1),
            (5, curses.COLOR_WHITE, -1),
            (6, curses.COLOR_BLUE, -1),
            (7, curses.COLOR_BLUE, -1),
            (8, curses.COLOR_WHITE, -1),
            (9, curses.COLOR_CYAN, -1),
            (10, curses.COLOR_WHITE, -1),
            (11, curses.COLOR_CYAN, -1),
            (12, curses.COLOR_BLUE, -1),
        ]
    },
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "price": 40,
        "colors": [
            (1, curses.COLOR_GREEN, -1),
            (2, curses.COLOR_YELLOW, -1),
            (3, curses.COLOR_RED, -1),
            (4, curses.COLOR_CYAN, -1),
            (5, curses.COLOR_WHITE, -1),
            (6, curses.COLOR_MAGENTA, -1),
            (7, curses.COLOR_BLUE, -1),
            (8, curses.COLOR_MAGENTA, -1),
            (9, curses.COLOR_YELLOW, -1),
            (10, curses.COLOR_WHITE, -1),
            (11, curses.COLOR_YELLOW, -1),
            (12, curses.COLOR_CYAN, -1),
        ]
    },
    "tokyo_night": {
        "name": "Tokyo Night Moon",
        "price": 45,
        "colors": [
            (1, curses.COLOR_BLUE, -1),
            (2, curses.COLOR_YELLOW, -1),
            (3, curses.COLOR_RED, -1),
            (4, curses.COLOR_CYAN, -1),
            (5, curses.COLOR_WHITE, -1),
            (6, curses.COLOR_MAGENTA, -1),
            (7, curses.COLOR_BLUE, -1),
            (8, curses.COLOR_BLUE, -1),
            (9, curses.COLOR_YELLOW, -1),
            (10, curses.COLOR_WHITE, -1),
            (11, curses.COLOR_YELLOW, -1),
            (12, curses.COLOR_CYAN, -1),
        ]
    }
}

# === SKINS ===

def _apply_cm(spr, cm):
    return [''.join(cm.get(c, c) for c in l) for l in spr]

def _build_skin(dino_cm, cactus_cm, bird_cm):
    return {
        "run1": _apply_cm(DINO_RUN1, dino_cm),
        "run2": _apply_cm(DINO_RUN2, dino_cm),
        "jump": _apply_cm(DINO_JUMP_SPRITE, dino_cm),
        "dead": _apply_cm(DINO_DEAD, dino_cm),
        "cactus_small": _apply_cm(CACTUS_SMALL, cactus_cm),
        "cactus_large": _apply_cm(CACTUS_LARGE, cactus_cm),
        "cactus_cluster": _apply_cm(CACTUS_CLUSTER, cactus_cm),
        "cactus_tall": _apply_cm(CACTUS_TALL, cactus_cm),
        "cactus_wavy": _apply_cm(CACTUS_WAVY, cactus_cm),
        "cactus_blossom": _apply_cm(CACTUS_BLOSSOM, cactus_cm),
        "bird_up": _apply_cm(BIRD_UP, bird_cm),
        "bird_down": _apply_cm(BIRD_DOWN, bird_cm),
    }

DINO_SKINS = {
    "classic": {
        "name": "Classic Dino", "price": 0,
        "colors": {"dino": 5, "cactus": 1, "bird": 6},
        "sprites": _build_skin({}, {}, {}),
    },
    "phantom": {
        "name": "Phantom", "price": 25,
        "colors": {"dino": 5, "cactus": 5, "bird": 5},
        "sprites": _build_skin(
            {"█": "░", "▓": "░", "▒": "░", "▌": "░", "▐": "░", "▄": "░"},
            {"█": "░", "▌": "░", "▐": "░", "▄": "░", "✿": "·"},
            {},
        ),
    },
    "ember": {
        "name": "Ember", "price": 40,
        "colors": {"dino": 3, "cactus": 3, "bird": 3},
        "sprites": _build_skin(
            {"█": "▓", "▒": "▓", "▌": "█", "▐": "█", "▄": "▓"},
            {"█": "▓", "▌": "█", "▐": "█", "▄": "▓", "✿": "*"},
            {},
        ),
    },
    "frost": {
        "name": "Frost", "price": 60,
        "colors": {"dino": 12, "cactus": 12, "bird": 12},
        "sprites": _build_skin(
            {"█": "▐", "▓": "▌", "▒": "░", "▌": "▌", "▐": "▐", "▄": "▀"},
            {"█": "▐", "▌": "▐", "▄": "▀", "✿": "◇"},
            {},
        ),
    },
}

SKIN_DINO_COLOR = 5
SKIN_CACTUS_COLOR = 1
SKIN_BIRD_COLOR = 6

def apply_skin(skin_id):
    global DINO_RUN1, DINO_RUN2, DINO_JUMP_SPRITE, DINO_DEAD
    global CACTUS_SMALL, CACTUS_LARGE, CACTUS_CLUSTER, CACTUS_TALL, CACTUS_WAVY, CACTUS_BLOSSOM
    global BIRD_UP, BIRD_DOWN
    global SKIN_DINO_COLOR, SKIN_CACTUS_COLOR, SKIN_BIRD_COLOR
    skin = DINO_SKINS.get(skin_id, DINO_SKINS["classic"])
    sp = skin["sprites"]
    DINO_RUN1 = sp["run1"]
    DINO_RUN2 = sp["run2"]
    DINO_JUMP_SPRITE = sp["jump"]
    DINO_DEAD = sp["dead"]
    CACTUS_SMALL = sp["cactus_small"]
    CACTUS_LARGE = sp["cactus_large"]
    CACTUS_CLUSTER = sp["cactus_cluster"]
    CACTUS_TALL = sp["cactus_tall"]
    CACTUS_WAVY = sp["cactus_wavy"]
    CACTUS_BLOSSOM = sp["cactus_blossom"]
    BIRD_UP = sp["bird_up"]
    BIRD_DOWN = sp["bird_down"]
    SKIN_DINO_COLOR = skin["colors"]["dino"]
    SKIN_CACTUS_COLOR = skin["colors"]["cactus"]
    SKIN_BIRD_COLOR = skin["colors"]["bird"]

# === HIGH SCORE & SAVE DATA ===
SAVE_FILE = os.path.expanduser("~/.dino_highscore.json")

def load_save_data():
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
            return {
                "high_score": data.get("high_score", 0),
                "total_coins": data.get("total_coins", 0),
                "unlocked_themes": data.get("unlocked_themes", ["classic"]),
                "current_theme": data.get("current_theme", "classic"),
                "unlocked_skins": data.get("unlocked_skins", ["classic"]),
                "current_skin": data.get("current_skin", "classic"),
                "muted": data.get("muted", False)
            }
    except Exception:
        return {
            "high_score": 0,
            "total_coins": 0,
            "unlocked_themes": ["classic"],
            "current_theme": "classic",
            "unlocked_skins": ["classic"],
            "current_skin": "classic",
            "muted": False
        }

def save_save_data(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
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

def apply_theme(theme_id):
    if theme_id not in THEMES:
        theme_id = "classic"
    theme = THEMES[theme_id]
    for pair_id, fg, bg in theme["colors"]:
        curses.init_pair(pair_id, fg, bg)

# === SHOP MENU ===

def show_shop(stdscr, save_data_dict, sound=None):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    current_tab = 0  # 0 = Themes, 1 = Skins
    selected_idx = 0
    theme_keys = list(THEMES.keys())
    skin_keys = list(DINO_SKINS.keys())
    original_theme = save_data_dict["current_theme"]
    original_skin = save_data_dict["current_skin"]
    confirmed = False

    apply_theme(theme_keys[0])
    apply_skin(skin_keys[0])

    while True:
        loop_start = time.monotonic()
        max_y, max_x = stdscr.getmaxyx()
        stdscr.erase()

        if max_y < 22 or max_x < 72:
            draw_centered(stdscr, max_y // 2, "Please expand your terminal to at least 72 columns!", max_x, curses.color_pair(3))
            stdscr.refresh()
            time.sleep(0.1)
            continue

        keys = theme_keys if current_tab == 0 else skin_keys
        items = THEMES if current_tab == 0 else DINO_SKINS
        current_key = save_data_dict["current_theme"] if current_tab == 0 else save_data_dict["current_skin"]
        unlocked_list = save_data_dict["unlocked_themes"] if current_tab == 0 else save_data_dict["unlocked_skins"]

        n = len(keys)
        if current_tab == 0:
            box_h = max(17, 10 + n)
        else:
            box_h = max(23, 19 + n)
        box_w = 70
        box_y = max_y // 2 - box_h // 2
        box_x = max_x // 2 - box_w // 2

        draw_solid_box(stdscr, box_y, box_x, box_h, box_w, 0)

        border_attr = curses.color_pair(4) | curses.A_BOLD
        try:
            stdscr.addstr(box_y, box_x, "╔" + "═" * (box_w - 2) + "╗", border_attr)
            for i in range(1, box_h - 1):
                stdscr.addstr(box_y + i, box_x, "║", border_attr)
                stdscr.addstr(box_y + i, box_x + box_w - 1, "║", border_attr)
            stdscr.addstr(box_y + box_h - 1, box_x, "╚" + "═" * (box_w - 2) + "╝", border_attr)
        except curses.error:
            pass

        draw_centered(stdscr, box_y + 1, "🛒 DINO ARCADIA SHOP 🛒", max_x, curses.color_pair(2) | curses.A_BOLD)
        draw_centered(stdscr, box_y + 2, f"Your Coins: ◉ {save_data_dict['total_coins']:03d}", max_x, curses.color_pair(11) | curses.A_BOLD)
        try:
            stdscr.addstr(box_y + 3, box_x + 2, "─" * (box_w - 4), curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass

        # Tab headers
        tab_labels = [" THEMES ", "  SKINS  "]
        tab_x_start = box_x + (box_w - 26) // 2
        for ti, label in enumerate(tab_labels):
            attr = curses.color_pair(6) | curses.A_BOLD | curses.A_REVERSE if ti == current_tab else curses.color_pair(5)
            try:
                stdscr.addstr(box_y + 4, tab_x_start + ti * 13, label, attr)
            except curses.error:
                pass

        content_start = box_y + 6
        first_pv_row = content_start

        for idx, key in enumerate(keys):
            item = items[key]
            price = item["price"]
            name = item["name"]
            py = content_start + idx

            if key == current_key:
                status = "[ EQUIPPED ]"
                status_color = curses.color_pair(1) | curses.A_BOLD
            elif key in unlocked_list:
                status = "[ UNLOCKED ]"
                status_color = curses.color_pair(4)
            else:
                status = f"◉ {price:03d} COINS"
                status_color = curses.color_pair(11)

            line_str = f" {name:<17} {status:>13} "
            if idx == selected_idx:
                try:
                    stdscr.addstr(py, box_x + 2, "▶", curses.color_pair(6) | curses.A_BOLD)
                    stdscr.addstr(py, box_x + 5, line_str, curses.color_pair(6) | curses.A_BOLD | curses.A_REVERSE)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(py, box_x + 5, line_str, status_color)
                except curses.error:
                    pass

            sep_x = box_x + 39
            try:
                stdscr.addstr(py, sep_x, "│", curses.color_pair(4) | curses.A_DIM)
            except curses.error:
                pass

            pv_x = box_x + 42
            if current_tab == 0:
                # Theme preview on right
                if idx == 0:
                    try:
                        stdscr.addstr(py, pv_x + 1, "*", curses.color_pair(2) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 4, "~", curses.color_pair(4) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 13, "★", curses.color_pair(9) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif idx == 1:
                    try:
                        stdscr.addstr(py, pv_x + 2, "◇", curses.color_pair(12) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 8, "▓", curses.color_pair(7) | curses.A_DIM)
                    except curses.error:
                        pass
                elif idx == 2:
                    try:
                        stdscr.addstr(py, pv_x + 3, "D", curses.color_pair(5) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 8, "▓", curses.color_pair(7) | curses.A_DIM)
                        stdscr.addstr(py, pv_x + 12, "▓", curses.color_pair(7) | curses.A_DIM)
                    except curses.error:
                        pass
                elif idx == 3:
                    try:
                        stdscr.addstr(py, pv_x + 2, "○", curses.color_pair(11) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 5, "█", curses.color_pair(1) | curses.A_BOLD)
                        stdscr.addstr(py, pv_x + 14, "█", curses.color_pair(1) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif idx == 4:
                    try:
                        stdscr.addstr(py, pv_x, "▁" * 24, curses.color_pair(1))
                    except curses.error:
                        pass
                elif idx == 5:
                    try:
                        stdscr.addstr(py, pv_x + 5, "◆ PREVIEW ◆", curses.color_pair(4) | curses.A_DIM)
                    except curses.error:
                        pass
            else:
                pass

        # Dedicated preview block for skins tab
        if current_tab == 1:
            # Draw separator on the gap row too
            gap_row = content_start + n
            sep_x = box_x + 39
            try:
                stdscr.addstr(gap_row, sep_x, "│", curses.color_pair(4) | curses.A_DIM)
            except curses.error:
                pass
            # Draw sprite preview
            preview_top = content_start + n + 1
            spr = items[keys[selected_idx]]["sprites"]["run1"]
            skin_color = items[keys[selected_idx]]["colors"]["dino"]
            for li, line in enumerate(spr):
                try:
                    stdscr.addstr(preview_top + li, pv_x, line, curses.color_pair(skin_color))
                except curses.error:
                    pass
                try:
                    stdscr.addstr(preview_top + li, sep_x, "│", curses.color_pair(4) | curses.A_DIM)
                except curses.error:
                    pass

        footer_row = content_start + n + (9 if current_tab == 1 else 0)
        try:
            stdscr.addstr(footer_row, box_x + 2, "─" * (box_w - 4), curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass

        try:
            stdscr.addstr(footer_row + 1, box_x + 2, "[ ← / → ] Tab     [ ↑ / ↓ ] Navigate     [ ENTER ] Buy / Equip", curses.color_pair(5))
        except curses.error:
            pass
        try:
            stdscr.addstr(footer_row + 2, box_x + 2, "[ Q / ESC ] Exit Shop", curses.color_pair(5))
        except curses.error:
            pass

        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            continue
        elif key in [27, ord('q'), ord('Q')]:
            break
        elif key in [curses.KEY_LEFT, ord('a'), ord('A')]:
            new_tab = (current_tab - 1) % 2
            if new_tab != current_tab:
                current_tab = new_tab
                selected_idx = 0
                preview_key = (theme_keys if current_tab == 0 else skin_keys)[selected_idx]
                if current_tab == 0:
                    apply_theme(preview_key)
                else:
                    apply_skin(preview_key)
        elif key in [curses.KEY_RIGHT, ord('d'), ord('D')]:
            new_tab = (current_tab + 1) % 2
            if new_tab != current_tab:
                current_tab = new_tab
                selected_idx = 0
                preview_key = (theme_keys if current_tab == 0 else skin_keys)[selected_idx]
                if current_tab == 0:
                    apply_theme(preview_key)
                else:
                    apply_skin(preview_key)
        elif key in [curses.KEY_UP, ord('w'), ord('W')]:
            selected_idx = (selected_idx - 1) % n
            preview_key = keys[selected_idx]
            if current_tab == 0:
                apply_theme(preview_key)
            else:
                apply_skin(preview_key)
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')]:
            selected_idx = (selected_idx + 1) % n
            preview_key = keys[selected_idx]
            if current_tab == 0:
                apply_theme(preview_key)
            else:
                apply_skin(preview_key)
        elif key in [10, 13, curses.KEY_ENTER, ord(' ')]:
            key_id = keys[selected_idx]
            if key_id in unlocked_list:
                if current_tab == 0:
                    save_data_dict["current_theme"] = key_id
                    apply_theme(key_id)
                else:
                    save_data_dict["current_skin"] = key_id
                    apply_skin(key_id)
                confirmed = True
                save_save_data(save_data_dict)
            else:
                price = items[key_id]["price"]
                if save_data_dict["total_coins"] >= price:
                    save_data_dict["total_coins"] -= price
                    unlocked_list.append(key_id)
                    if current_tab == 0:
                        save_data_dict["current_theme"] = key_id
                        apply_theme(key_id)
                    else:
                        save_data_dict["current_skin"] = key_id
                        apply_skin(key_id)
                    confirmed = True
                    save_save_data(save_data_dict)
                    if sound:
                        sound.purchase()
                else:
                    if sound:
                        sound.error()
                    if not save_data_dict["muted"]:
                        try:
                            curses.flash()
                        except curses.error:
                            pass

        elapsed = time.monotonic() - loop_start
        time.sleep(max(0, 0.03 - elapsed))

    if not confirmed:
        apply_theme(original_theme)
        apply_skin(original_skin)
        save_data_dict["current_theme"] = original_theme
        save_data_dict["current_skin"] = original_skin

# === SOUND SYSTEM ===

class SoundSystem:
    _temp_files = []

    @classmethod
    def cleanup(cls):
        for f in cls._temp_files:
            try:
                os.unlink(f)
            except Exception:
                pass

    def __init__(self, muted=False):
        self.muted = muted

    def _play(self, wav_data):
        if self.muted:
            return
        try:
            tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            tmp.write(wav_data)
            name = tmp.name
            tmp.close()
            self._temp_files.append(name)
            try:
                subprocess.Popen(['aplay', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                try:
                    subprocess.Popen(['paplay', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    pass
        except Exception:
            pass

    def _sine(self, freq, dur, vol=0.3, rate=22050):
        n = int(dur * rate)
        return struct.pack('<' + 'h' * n, *[
            int(vol * (1 - i / n * 0.4) * 32767 * math.sin(2 * math.pi * freq * i / rate))
            for i in range(n)
        ])

    def _sweep(self, f0, f1, dur, vol=0.3, rate=22050):
        n = int(dur * rate)
        return struct.pack('<' + 'h' * n, *[
            int(vol * (1 - i / n * 0.5) * 32767 * math.sin(2 * math.pi * (f0 + (f1 - f0) * i / n) * i / rate))
            for i in range(n)
        ])

    def _noise(self, dur, vol=0.3, rate=22050):
        n = int(dur * rate)
        return struct.pack('<' + 'h' * n, *[
            int(vol * (1 - i / n * 0.7) * 32767 * random.uniform(-1, 1))
            for i in range(n)
        ])

    def _wav(self, frames, rate=22050):
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(frames)
        return buf.getvalue()

    def jump(self):
        self._play(self._wav(self._sweep(350, 700, 0.1)))

    def double_jump(self):
        self._play(self._wav(self._sweep(500, 950, 0.08)))

    def coin(self):
        s1 = self._sine(1400, 0.05, 0.25)
        self._play(self._wav(s1 + b'\x00' * 400 + self._sine(1800, 0.06, 0.2)))

    def shield(self):
        s = self._sine(500, 0.06) + b'\x00' * 200 + self._sine(700, 0.06) + b'\x00' * 200 + self._sine(900, 0.06)
        self._play(self._wav(s))

    def magnet(self):
        self._play(self._wav(self._sweep(400, 800, 0.2)))

    def slow_mo(self):
        self._play(self._wav(self._sweep(500, 200, 0.25)))

    def shield_deflect(self):
        n = self._noise(0.15, 0.35)
        s = self._sweep(600, 150, 0.15)
        frames = bytearray(max(len(n), len(s)))
        for i in range(0, len(frames) - 1, 2):
            vn = struct.unpack('<h', n[i:i+2])[0] if i < len(n) else 0
            vs = struct.unpack('<h', s[i:i+2])[0] if i < len(s) else 0
            v = max(-32767, min(32767, (vn + vs) // 2))
            struct.pack_into('<h', frames, i, v)
        self._play(self._wav(bytes(frames)))

    def game_over(self):
        self._play(self._wav(self._sweep(500, 80, 0.5, 0.4)))

    def milestone(self):
        s1 = self._sine(800, 0.08)
        s2 = self._sine(1050, 0.08)
        frames = bytearray(max(len(s1), len(s2)))
        for i in range(0, len(frames) - 1, 2):
            v1 = struct.unpack('<h', s1[i:i+2])[0] if i < len(s1) else 0
            v2 = struct.unpack('<h', s2[i:i+2])[0] if i < len(s2) else 0
            v = max(-32767, min(32767, (v1 + v2) // 2))
            struct.pack_into('<h', frames, i, v)
        self._play(self._wav(bytes(frames)))

    def near_miss(self):
        w = self._sweep(700, 950, 0.06) + self._sweep(950, 600, 0.06)
        self._play(self._wav(w))

    def purchase(self):
        s = self._sine(550, 0.06) + b'\x00' * 200 + self._sine(750, 0.06) + b'\x00' * 200 + self._sine(950, 0.06)
        self._play(self._wav(s))

    def error(self):
        self._play(self._wav(self._sine(150, 0.15, 0.2)))

atexit.register(SoundSystem.cleanup)

# === MAIN GAME ===

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    curses.start_color()
    curses.use_default_colors()

    # Load initial save data
    sd = load_save_data()
    high_score = sd["high_score"]

    # Initial apply theme
    apply_theme(sd["current_theme"])

    max_y, max_x = stdscr.getmaxyx()

    ground_y = max_y - 4
    dino_x = 8
    dino_base_y = ground_y - len(DINO_RUN1)

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
        shooting_stars = []
        
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

        # Saved stats/customization loaded from file
        total_coins = sd["total_coins"]
        unlocked_themes = sd["unlocked_themes"]
        current_theme = sd["current_theme"]
        unlocked_skins = sd["unlocked_skins"]
        current_skin = sd["current_skin"]
        muted = sd["muted"]

    s = State()
    apply_skin(s.current_skin)
    sound = SoundSystem(muted=s.muted)

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
        s.shooting_stars = []

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

        # Mute/Unmute toggle
        if ord('m') in pressed or ord('M') in pressed:
            s.muted = not s.muted
            sound.muted = s.muted
            sd_save = {
                "high_score": high_score,
                "total_coins": s.total_coins,
                "unlocked_themes": s.unlocked_themes,
                "current_theme": s.current_theme,
                "unlocked_skins": s.unlocked_skins,
                "current_skin": s.current_skin,
                "muted": s.muted
            }
            save_save_data(sd_save)

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

                # Open shop
                if ord('s') in pressed or ord('S') in pressed:
                    sd_shop = {
                        "high_score": high_score,
                        "total_coins": s.total_coins,
                        "unlocked_themes": s.unlocked_themes,
                        "current_theme": s.current_theme,
                        "unlocked_skins": s.unlocked_skins,
                        "current_skin": s.current_skin,
                        "muted": s.muted
                    }
                    show_shop(stdscr, sd_shop, sound)
                    # Sync shop modifications
                    high_score = sd_shop["high_score"]
                    s.total_coins = sd_shop["total_coins"]
                    s.unlocked_themes = sd_shop["unlocked_themes"]
                    s.current_theme = sd_shop["current_theme"]
                    s.unlocked_skins = sd_shop["unlocked_skins"]
                    s.current_skin = sd_shop["current_skin"]
                    s.muted = sd_shop["muted"]
                    # Apply any updated theme/skin
                    apply_theme(s.current_theme)
                    apply_skin(s.current_skin)

            # Jump / Double-Jump input trigger
            if ord(' ') in pressed or curses.KEY_UP in pressed or ord('w') in pressed or ord('W') in pressed:
                if not s.jumping:
                    s.jumping = True
                    s.started = True
                    s.jump_vel = JUMP_STRENGTH
                    s.double_jumped = False
                    sound.jump()
                    # Spawn jump ground puff particles
                    spawn_particles(dino_x + 3, ground_y - 1, count=5, 
                                    color=curses.color_pair(4) | curses.A_DIM, chars=[".", "~", "o"])
                elif not s.double_jumped:
                    # Double jump in mid-air!
                    s.jump_vel = DOUBLE_JUMP_STRENGTH
                    s.double_jumped = True
                    sound.double_jump()
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

            # Running Dust Trails behind Dino's feet
            if s.frame % 6 == 0 and not s.jumping:
                spawn_particles(dino_x + 1, ground_y - 1, count=1, 
                                color=curses.color_pair(1) | curses.A_DIM, chars=[".", "~", "o"])

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
            eff_speed = s.speed * s.slow_factor
            for obs in s.obstacles:
                obs["x"] -= eff_speed
            s.obstacles = [o for o in s.obstacles if o["x"] > -15]

            # Helper: check if spawn x is too close to any existing obstacle
            def safe_to_spawn(spawn_x, min_dist=30):
                for obs in s.obstacles:
                    if abs(obs["x"] - spawn_x) < min_dist:
                        return False
                return True

            # Spawning Coins
            s.coin_spawn_timer += 1
            if s.coin_spawn_timer >= random.randint(35, 75):
                s.coin_spawn_timer = 0
                spawn_x = float(max_x + 2)
                if safe_to_spawn(spawn_x, min_dist=35):
                    coin_y_choices = [ground_y - 3, ground_y - 6, ground_y - 9]
                    s.coins.append({
                        "x": spawn_x,
                        "y": float(random.choice(coin_y_choices))
                    })

            # Spawning Power-ups
            s.powerup_spawn_timer += 1
            if s.powerup_spawn_timer >= random.randint(320, 580):
                s.powerup_spawn_timer = 0
                spawn_x = float(max_x + 2)
                if safe_to_spawn(spawn_x, min_dist=40):
                    r = random.random()
                    if s.speed >= 2.7:
                        if r < 0.33:
                            pup_type = "shield"
                        elif r < 0.66:
                            pup_type = "magnet"
                        else:
                            pup_type = "slow"
                    else:
                        pup_type = "shield" if r < 0.5 else "magnet"
                    s.powerups.append({
                        "type": pup_type,
                        "x": spawn_x,
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
                        pull_speed = s.speed * 1.4
                        coin["x"] += (dx_vec / dist) * pull_speed
                        coin["y"] += (dy_vec / dist) * pull_speed
                    else:
                        coin["x"] -= eff_speed
                else:
                    coin["x"] -= eff_speed
            s.coins = [c for c in s.coins if c["x"] > -5]

            # Move Power-ups
            for pup in s.powerups:
                pup["x"] -= eff_speed
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

            if s.slow_active:
                s.slow_timer -= 1
                if s.slow_timer <= 0:
                    s.slow_active = False
                    s.slow_factor = 1.0
                    s.combo_texts.append({
                        "text": "SLOW-MO EXPIRED",
                        "x": float(dino_x),
                        "y": s.dino_y - 1,
                        "vy": -0.3,
                        "life": 30,
                        "color": curses.color_pair(6) | curses.A_DIM
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

            # Spawn shooting stars occasionally at night
            if s.is_night and random.random() < 0.005 and len(s.shooting_stars) < 2:
                s.shooting_stars.append({
                    "x": float(random.randint(max_x // 3, max_x)),
                    "y": float(random.randint(1, ground_y // 3)),
                    "vx": random.uniform(-1.5, -0.8),
                    "vy": random.uniform(0.3, 0.6),
                    "life": random.randint(20, 40)
                })
                
            # Update shooting stars
            for ss in s.shooting_stars:
                ss["x"] += ss["vx"]
                ss["y"] += ss["vy"]
                ss["life"] -= 1
            s.shooting_stars = [ss for ss in s.shooting_stars if ss["life"] > 0]

            # Incremental Score
            if s.frame % 3 == 0:
                s.score += 1

            # Milestone Flashing (Every 100 points)
            if s.score // 100 > s.last_milestone:
                s.last_milestone = s.score // 100
                s.milestone_flash = 30
                sound.milestone()

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

            # --- Collision Rects Calculations ---
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
                    s.total_coins += 1
                    coin_val = 15 + (5 * s.combo)
                    s.score += coin_val
                    sound.coin()
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
                        sound.shield()
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
                        sound.magnet()
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
                    elif pup["type"] == "slow":
                        s.slow_active = True
                        s.slow_timer = SLOW_DURATION
                        s.slow_factor = 0.70
                        sound.slow_mo()
                        spawn_particles(pup["x"] + 1, pup["y"] + 1, count=12,
                                        color=curses.color_pair(6) | curses.A_BOLD, chars=["~", "·", "s", "*"])
                        s.combo_texts.append({
                            "text": "SLOW-MO ACTIVATED!",
                            "x": float(dino_x),
                            "y": s.dino_y - 2,
                            "vy": -0.3,
                            "life": 40,
                            "color": curses.color_pair(6) | curses.A_BOLD
                        })
                    if not s.muted:
                        try:
                            curses.flash()
                        except curses.error:
                            pass
                else:
                    remaining_pups.append(pup)
            s.powerups = remaining_pups

            # Check Obstacles Collisions & Near Misses
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
                        s.shield_active = False
                        s.shield_timer = 0
                        s.shake_frames = 12
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
                        sound.shield_deflect()
                        if not s.muted:
                            try:
                                curses.flash()
                            except curses.error:
                                pass
                        continue
                    else:
                        s.game_over = True
                        s.shake_frames = 12
                        spawn_particles(dino_x + 4, cur_y + 3, count=15, 
                                        color=curses.color_pair(3) | curses.A_BOLD)
                        sound.game_over()
                        if not s.muted:
                            try:
                                curses.flash()
                            except curses.error:
                                pass
                        
                        # Save score and coins
                        sd_save = {
                            "high_score": max(high_score, s.score),
                            "total_coins": s.total_coins,
                            "unlocked_themes": s.unlocked_themes,
                            "current_theme": s.current_theme,
                            "unlocked_skins": s.unlocked_skins,
                            "current_skin": s.current_skin,
                            "muted": s.muted
                        }
                        if s.score > high_score:
                            high_score = s.score
                            s.new_high = True
                        save_save_data(sd_save)
                
                # 2. Near Miss detection
                elif not obs.get("near_missed", False):
                    dino_right = dino_x + 2 + len(cur_sprite[0]) - 4
                    if dino_right <= ox <= dino_right + 2:
                        dino_top = cur_y + 1
                        dino_bot = cur_y + 1 + dh
                        obs_top = oy
                        obs_bot = oy + len(sprite)
                        if dino_top < obs_bot and dino_bot > obs_top:
                            obs["near_missed"] = True
                            s.near_misses += 1
                            s.combo += 1
                            s.combo_timer = 120
                            near_bonus = 50 * s.combo
                            s.score += near_bonus
                            sound.near_miss()
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

        if max_y < 22 or max_x < 60:
            draw_centered(stdscr, max_y // 2 - 1, "┌─────────────────────────────────────┐", max_x, curses.color_pair(3))
            draw_centered(stdscr, max_y // 2,     "│  ⚠️  TERMINAL WINDOW TOO SMALL!      │", max_x, curses.color_pair(3) | curses.A_BOLD)
            draw_centered(stdscr, max_y // 2 + 1, "│  Please expand to at least 60x22    │", max_x, curses.color_pair(5))
            draw_centered(stdscr, max_y // 2 + 2, "└─────────────────────────────────────┘", max_x, curses.color_pair(3))
            stdscr.refresh()
            elapsed = time.monotonic() - loop_start
            time.sleep(max(0, 0.028 - elapsed))
            continue

        # Stars in Night Sky
        if s.is_night:
            for star in s.stars:
                if (s.frame + star["blink"]) % 40 < 30:
                    try:
                        stdscr.addstr(star["y"], star["x"], star["ch"],
                                      curses.color_pair(9) | curses.A_DIM)
                    except curses.error:
                        pass

        # Draw shooting stars
        if s.is_night:
            for ss in s.shooting_stars:
                sx_ss, sy_ss = int(ss["x"]), int(ss["y"])
                if 0 < sx_ss < max_x - 1 and 0 <= sy_ss < max_y:
                    try:
                        stdscr.addstr(sy_ss, sx_ss, "★", curses.color_pair(10) | curses.A_BOLD)
                        trail_x = int(ss["x"] - ss["vx"])
                        trail_y = int(ss["y"] - ss["vy"])
                        if 0 < trail_x < max_x - 1 and 0 <= trail_y < max_y:
                            stdscr.addstr(trail_y, trail_x, ".", curses.color_pair(10) | curses.A_DIM)
                    except curses.error:
                        pass

        # Sliding Celestial Objects
        if not s.is_night:
            progress = s.night_timer / (DAY_LENGTH // 2)
            sun_x = int(max_x - progress * (max_x + 15))
            draw_sprite(stdscr, 2 + shake_y, sun_x + sx, SUN, max_y, max_x, curses.color_pair(2) | curses.A_BOLD)
        else:
            progress = (s.night_timer - DAY_LENGTH // 2) / (DAY_LENGTH // 2)
            moon_x = int(max_x - progress * (max_x + 15))
            draw_sprite(stdscr, 2 + shake_y, moon_x + sx, MOON, max_y, max_x, curses.color_pair(10) | curses.A_BOLD)

        # Mountains
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

        # Draw Obstacles
        for obs in s.obstacles:
            ox = int(obs["x"]) + sx
            if obs["type"] == "cactus_small":
                draw_sprite(stdscr, gy - len(CACTUS_SMALL), ox, CACTUS_SMALL,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            elif obs["type"] == "cactus_large":
                draw_sprite(stdscr, gy - len(CACTUS_LARGE), ox, CACTUS_LARGE,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            elif obs["type"] == "cactus_cluster":
                draw_sprite(stdscr, gy - len(CACTUS_CLUSTER), ox, CACTUS_CLUSTER,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            elif obs["type"] == "cactus_tall":
                draw_sprite(stdscr, gy - len(CACTUS_TALL), ox, CACTUS_TALL,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            elif obs["type"] == "cactus_wavy":
                draw_sprite(stdscr, gy - len(CACTUS_WAVY), ox, CACTUS_WAVY,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            elif obs["type"] == "cactus_blossom":
                draw_sprite(stdscr, gy - len(CACTUS_BLOSSOM), ox, CACTUS_BLOSSOM,
                            max_y, max_x, curses.color_pair(SKIN_CACTUS_COLOR))
            else:  # Bird
                bird_sprite = BIRD_UP if s.frame % 14 < 7 else BIRD_DOWN
                draw_sprite(stdscr, obs["y"] + shake_y, ox, bird_sprite,
                            max_y, max_x, curses.color_pair(SKIN_BIRD_COLOR))

        # Draw Coins
        for coin in s.coins:
            draw_sprite(stdscr, int(coin["y"]) + shake_y, int(coin["x"]) + sx, COIN,
                        max_y, max_x, curses.color_pair(11) | curses.A_BOLD)

        # Draw Power-ups
        for pup in s.powerups:
            if pup["type"] == "shield":
                pup_sprite = SHIELD_ICON
                pup_color = curses.color_pair(12)
            elif pup["type"] == "slow":
                pup_sprite = SLOW_ICON
                pup_color = curses.color_pair(6)
            else:
                pup_sprite = MAGNET_ICON
                pup_color = curses.color_pair(6)
            draw_sprite(stdscr, int(pup["y"]) + shake_y, int(pup["x"]) + sx, pup_sprite,
                        max_y, max_x, pup_color | curses.A_BOLD)

        # Draw Dino
        if s.game_over:
            dino_sprite = DINO_DEAD
            dy = int(s.dino_y) + shake_y
        elif s.jumping:
            dino_sprite = DINO_JUMP_SPRITE
            dy = int(s.dino_y) + shake_y
        else:
            dino_sprite = DINO_RUN1 if s.frame % 8 < 4 else DINO_RUN2
            dy = int(s.dino_y) + shake_y

        dino_attr = curses.color_pair(SKIN_DINO_COLOR) | curses.A_BOLD
        draw_sprite(stdscr, dy, dino_x + sx, dino_sprite, max_y, max_x, dino_attr)

        # --- Draw Dino Power-up Auric Overlay Effects ---
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

        # Mute status indicator
        snd_str = "[🔇 Muted]" if s.muted else "[🔊 Sound]"
        try:
            stdscr.addstr(3, max_x - len(snd_str) - 2, snd_str, curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass

        # Day/Night phase indicator
        indicator = " NIGHT" if s.is_night else " DAY"
        try:
            stdscr.addstr(1, 2, indicator, curses.color_pair(9 if s.is_night else 2) | curses.A_BOLD)
        except curses.error:
            pass

        # Coins collected HUD icon
        coins_str = f"◉ {s.coins_collected:03d} COINS  (Total: ◉ {s.total_coins:03d})"
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

        # Start Screen Title Overlay
        if not s.started and not s.game_over:
            ty = max_y // 2 - 8
            card_w = 66
            card_x = max(0, max_x // 2 - card_w // 2)
            draw_solid_box(stdscr, ty - 1, card_x, 18, card_w, 0)

            for i, line in enumerate(TITLE_ART):
                draw_centered(stdscr, ty + i, line, max_x, curses.color_pair(2) | curses.A_BOLD)

            draw_centered(stdscr, ty + len(TITLE_ART) + 1,
                          "[ SPACE / ↑ / W ] Jump / Double-Jump      [ P ] Pause      [ M ] Mute", max_x, curses.color_pair(5))
            draw_centered(stdscr, ty + len(TITLE_ART) + 2,
                          "[ S ] Shop & Customization      [ Q / ESC ] Quit Game", max_x, curses.color_pair(5))

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

        # Pause Menu Overlay
        if s.paused:
            card_x = max(0, max_x // 2 - 11)
            draw_solid_box(stdscr, max_y // 2 - 2, card_x, 5, 22, 0)

            draw_centered(stdscr, max_y // 2 - 1,
                          "┌───────────────────┐", max_x, curses.color_pair(2))
            draw_centered(stdscr, max_y // 2,
                          "│     || PAUSED     │", max_x, curses.color_pair(2) | curses.A_BOLD)
            draw_centered(stdscr, max_y // 2 + 1,
                          "└───────────────────┘", max_x, curses.color_pair(2))

        # Game Over Overlay
        if s.game_over:
            cy = max_y // 2 - 4
            box_x = max(0, max_x // 2 - 14)
            card_x = max(0, max_x // 2 - 15)
            
            draw_solid_box(stdscr, cy - 1, card_x, 9, 30, 0)

            box_color = curses.color_pair(3)
            draw_centered(stdscr, cy,     "┌──────────────────────────┐", max_x, box_color)
            draw_centered(stdscr, cy + 1, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 2, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 3, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 4, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 5, "│                          │", max_x, box_color)
            draw_centered(stdscr, cy + 6, "└──────────────────────────┘", max_x, box_color)

            text_x = box_x + 1
            
            try:
                stdscr.addstr(cy + 1, text_x, "       GAME OVER!         ", curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass

            score_val_str = f"{s.score:05d}"
            try:
                stdscr.addstr(cy + 2, text_x, f"    Score:  {score_val_str:<14}", curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

            coins_val_str = f"{s.coins_collected:03d}"
            try:
                stdscr.addstr(cy + 3, text_x, f"    Coins:  {coins_val_str:<14}", curses.color_pair(11) | curses.A_BOLD)
            except curses.error:
                pass

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
