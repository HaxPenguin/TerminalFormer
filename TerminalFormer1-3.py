import curses
import time
import os
import random
import time

# =============================================================================
# Constants (shared between game & editor)
# =============================================================================
SCORE_FILE    = "scores.txt"
MAX_SCORES    = 5
CUSTOM_FOLDER = "custom_levels"
LEVEL_WIDTH   = 80
LEVEL_HEIGHT  = 11
EMPTY_CHAR    = " "
GRAVITY       = 1
JUMP_VELOCITY = -2.5
MOVE_SPEED    = 2
FPS           = 15

# Ensure the custom_levels folder exists
os.makedirs(CUSTOM_FOLDER, exist_ok=True)

# =============================================================================
# Built-in levels (unchanged)
# =============================================================================
game_levels = [
    [
        "                                                                                ",
        "                R to reset        lvl 1                                         ",
        "                l to leave                                                      ",
        "                                                                                ",
        "                                ▒▒▒▒                                            ",
        "                                        ▒                                       ",
        "                          ▒▒▒▒          ▒                                       ",
        "                                        ▒                                       ",
        "                     ▒▒▒▒               ▒                 ▒                     ",
        "                                        ▒                 ▒                     ",
        "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
    ],
    [
        "      ▒▒▒▒▒                                  ▒                                  ",
        "      ▒                  lvl 2               ▒                                  ",
        "      ▒                                      ▒                                  ",
        "      ▒        ▒                          ▒▒ ▒                                  ",
        "      ▒        ▒                          ▒  ▒                                  ",
        "      ▒   ▒▒▒▒▒▒                         ▒▒ ▒▒                                  ",
        "      ▒▒  ▒                               ▒  ▒                                  ",
        "      ▒   ▒        ▒▒▒▒              ▒▒▒▒▒▒                                     ",
        "      ▒  ▒▒           ▒      ▒▒▒▒    ▒▒   ▒▒▒▒▒▒                               ",
        "          ▒           ▒      ▒  ▒    ▒▒         ▒                               ",
        "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
    ],
    [
        "                                                                                ",
        "                             lvl 3                                              ",
        "                                                                                ",
        "                                                                                ",
        "                                        ▒      ▒                                ",
        "                                       ▒   ▒▒   ▒                               ",
        "         ▒    ▒  ▒▒▒▒▒                   ▒    ▒                                 ",
        "         ▒▒▒▒▒▒    ▒                        ▒                                   ",
        "        ▒▒    ▒    ▒                                                            ",
        "         ▒    ▒  ▒▒▒▒▒                                                          ",
        "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
    ]
]

# =============================================================================
# High-score management (unchanged)
# =============================================================================
def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE) as f:
        return [float(line.strip()) for line in f if line.strip()]

def save_score(new_time):
    scores = sorted(load_scores() + [new_time])[:MAX_SCORES]
    with open(SCORE_FILE, "w") as f:
        f.writelines(f"{s:.2f}\n" for s in scores)

# =============================================================================
# Custom-level loading for the game (unchanged)
# =============================================================================
def load_custom_levels():
    levels = []
    for fn in sorted(os.listdir(CUSTOM_FOLDER)):
        path = os.path.join(CUSTOM_FOLDER, fn)
        if not os.path.isfile(path):
            continue
        try:
            raw = open(path).readlines()
        except OSError:
            continue
        rows = [
            (raw[i].rstrip("\n") if i < len(raw) else "")
            .ljust(LEVEL_WIDTH, EMPTY_CHAR)[:LEVEL_WIDTH]
            for i in range(LEVEL_HEIGHT)
        ]
        levels.append((fn, rows))
    return levels

# =============================================================================
# Level editor functions
# =============================================================================
def create_blank_level():
    # Philosophical blank canvas—but with a solid floor :P
    return [EMPTY_CHAR * LEVEL_WIDTH for _ in range(LEVEL_HEIGHT - 1)] + ["#" * LEVEL_WIDTH]

def load_level_for_editing(filename):
    path = os.path.join(CUSTOM_FOLDER, filename)
    if not os.path.isfile(path):
        return create_blank_level()
    with open(path) as f:
        raw = f.readlines()
    return [
        (raw[i].rstrip("\n") if i < len(raw) else "").ljust(LEVEL_WIDTH, EMPTY_CHAR)[:LEVEL_WIDTH]
        for i in range(LEVEL_HEIGHT)
    ]

def save_level_from_editor(level_data, filename):
    path = os.path.join(CUSTOM_FOLDER, filename)
    try:
        with open(path, "w") as f:
            for row in level_data:
                f.write(row + "\n")
    except OSError:
        pass  # Silently fail—curses UI will forgive us ;)

import random

def level_editor_main(stdscr):
    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.keypad(True)

    options = ["Create New Level", "Edit Existing Level", "Back to Main Menu"]
    idx = 0

    # Pick a random custom level for background (if any)
    customs = load_custom_levels()
    if customs:
        _, bg_map = random.choice(customs)
    else:
        bg_map = None

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw dimmed background
        if bg_map:
            off_y = max((h - LEVEL_HEIGHT) // 2, 0)
            off_x = max((w - LEVEL_WIDTH) // 2, 0)
            for y, row in enumerate(bg_map):
                for x, ch in enumerate(row):
                    stdscr.addch(off_y + y, off_x + x, ch, curses.A_DIM)

        # --- Editor menu centered ---
        menu_height = len(options) + 1  # title + options
        start_y = (h - menu_height) // 2

        # Title
        title = "Level Editor"
        stdscr.addstr(start_y,
                      (w - len(title)) // 2,
                      title,
                      curses.A_BOLD)

        # Options
        for i, opt in enumerate(options):
            y = start_y + 1 + i
            x = (w - len(opt)) // 2
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(y, x, opt, attr)

        stdscr.refresh()
        key = stdscr.getch()

        # Navigate menu
        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(options) - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, ord("\n")):
            if idx == 2:
                return  # Back to main menu

            # New or existing?
            if idx == 0:
                filename = f"level_{int(time.time())}.txt"
                level_data = create_blank_level()
            else:
                files = sorted(os.listdir(CUSTOM_FOLDER))
                if not files:
                    msg = "(no levels to edit)"
                    stdscr.addstr(h - 2,
                                  (w - len(msg)) // 2,
                                  msg, curses.A_DIM)
                    stdscr.getch()
                    continue

                sel = 0
                while True:
                    stdscr.clear()
                    # Draw same background underneath submenu
                    if bg_map:
                        for y, row in enumerate(bg_map):
                            for x, ch in enumerate(row):
                                stdscr.addch(off_y + y, off_x + x, ch, curses.A_DIM)

                    # File‐selection centered
                    list_height = len(files) + 1
                    sub_start_y = (h - list_height) // 2

                    header = "Select Level File (q to cancel)"
                    stdscr.addstr(sub_start_y,
                                  (w - len(header)) // 2,
                                  header, curses.A_BOLD)

                    for j, fn in enumerate(files):
                        y = sub_start_y + 1 + j
                        x = (w - len(fn)) // 2
                        attr = curses.A_REVERSE if j == sel else curses.A_NORMAL
                        stdscr.addstr(y, x, fn, attr)

                    stdscr.refresh()
                    k = stdscr.getch()
                    if k == curses.KEY_UP and sel > 0:
                        sel -= 1
                    elif k == curses.KEY_DOWN and sel < len(files) - 1:
                        sel += 1
                    elif k in (curses.KEY_ENTER, ord("\n")):
                        filename = files[sel]
                        level_data = load_level_for_editing(filename)
                        break
                    elif k == ord("q"):
                        filename = None
                        break

                if filename is None:
                    continue

            # --- Begin editing session, grid centered ---
            cursor_y, cursor_x = 0, 0
            off_y = (h - LEVEL_HEIGHT) // 2
            off_x = (w - LEVEL_WIDTH) // 2

            while True:
                stdscr.clear()
                # Redraw background under grid
                if bg_map:
                    for y, row in enumerate(bg_map):
                        for x, ch in enumerate(row):
                            stdscr.addch(off_y + y, off_x + x, ch, curses.A_DIM)

                # Draw level grid
                for y, row in enumerate(level_data):
                    for x, ch in enumerate(row):
                        attr = curses.A_REVERSE if (y == cursor_y and x == cursor_x) else curses.A_NORMAL
                        stdscr.addch(off_y + y, off_x + x, ch, attr)

                # Hint line centered below grid
                hint = "Arrows=move  Space=toggle  s=save  q=quit"
                stdscr.addstr(off_y + LEVEL_HEIGHT + 1,
                              (w - len(hint)) // 2,
                              hint,
                              curses.A_DIM)

                stdscr.refresh()
                k = stdscr.getch()

                if k == ord("q"):
                    break
                elif k == ord("s"):
                    save_level_from_editor(level_data, filename)
                    break
                elif k == curses.KEY_UP and cursor_y > 0:
                    cursor_y -= 1
                elif k == curses.KEY_DOWN and cursor_y < LEVEL_HEIGHT - 1:
                    cursor_y += 1
                elif k == curses.KEY_LEFT and cursor_x > 0:
                    cursor_x -= 1
                elif k == curses.KEY_RIGHT and cursor_x < LEVEL_WIDTH - 1:
                    cursor_x += 1
                elif k == ord(" "):
                    if cursor_y < LEVEL_HEIGHT - 1:
                        row = list(level_data[cursor_y])
                        row[cursor_x] = "▒" if row[cursor_x] == EMPTY_CHAR else EMPTY_CHAR
                        level_data[cursor_y] = "".join(row)

# =============================================================================
# Game rendering & input (unchanged)
# =============================================================================
def draw_custom_selection(stdscr):
    choices = load_custom_levels()  # list of (filename, rows)
    if not choices:
        return None

    idx = 0
    n = len(choices)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Compute vertical centering: 1 title + n options
        menu_height = 1 + n
        start_y = (h - menu_height) // 2

        # Centered title
        title = "Select Custom Level (q=cancel)"
        stdscr.addstr(start_y,
                      (w - len(title)) // 2,
                      title, curses.A_BOLD)

        # Centered options
        for i, (fn, _) in enumerate(choices):
            y = start_y + 1 + i
            x = (w - len(fn)) // 2
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(y, x, fn, attr)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < n - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, ord("\n")):
            return choices[idx][1]
        elif key == ord("q"):
            return None

def draw_game(stdscr, level_map, timer):
    level_map = [r.ljust(LEVEL_WIDTH, EMPTY_CHAR)[:LEVEL_WIDTH] for r in level_map]
    curses.curs_set(0); stdscr.nodelay(1); stdscr.timeout(1000//FPS)
    H, W = LEVEL_HEIGHT, LEVEL_WIDTH
    win_h,win_w = stdscr.getmaxyx()
    off_y,off_x = max((win_h-H)//2,0), max((win_w-W)//2,0)
    px,py,vy = 2, H-2, 0; on_ground=False

    while True:
        stdscr.clear()
        for y,row in enumerate(level_map):
            stdscr.addstr(off_y+y, off_x, row)
        elapsed = time.time() - timer.get("start",0) if timer.get("start") else 0.0
        stdscr.addstr(0, win_w-13, f"Time: {elapsed:05.2f}s")
        key = stdscr.getch()
        if key == ord("l"):
            return False
        if key == ord("r"):
            return None

        move_left, move_right, jump = (
            key == curses.KEY_LEFT,
            key == curses.KEY_RIGHT,
            key == ord(" ")
        )
        if timer.get("start") is None and (move_left or move_right or jump):
            timer["start"] = time.time()

        if jump and on_ground:
            vy, on_ground = JUMP_VELOCITY, False

        vy += GRAVITY
        new_py = py + vy

        # vertical collision
        if vy > 0:
            for ytest in range(py+1, int(new_py)+1):
                if level_map[min(ytest,H-1)][px] in "▒#":
                    new_py, vy, on_ground = ytest-1, 0, True
                    break
        elif vy < 0:
            for ytest in range(py-1, int(new_py)-1, -1):
                if level_map[max(ytest,0)][px] in "▒#":
                    new_py, vy = ytest+1, 0
                    break
        py = max(0, min(H-1, int(new_py)))

        # horizontal movement
        if move_left:
            for _ in range(MOVE_SPEED):
                if px>0 and level_map[py][px-1] not in "▒#":
                    px-=1
        if move_right:
            for _ in range(MOVE_SPEED):
                if px+1<W and level_map[py][px+1] not in "▒#":
                    px+=1

        stdscr.addch(off_y+py, off_x+px, "#")
        stdscr.refresh()
        time.sleep(1/FPS)
        if px >= W-1:
            return True

def draw_win(stdscr, final_time):
    curses.curs_set(0); stdscr.nodelay(0); stdscr.clear()
    h,w = stdscr.getmaxyx()
    msgs = ["You Win!", f"Final time: {final_time:05.2f}s", "Press Enter to exit"]
    for i,m in enumerate(msgs):
        stdscr.addstr((h-len(msgs))//2+i, (w-len(m))//2,
                      m, curses.A_BOLD if i==0 else curses.A_NORMAL)
    stdscr.refresh(); curses.flushinp()
    while stdscr.getch() not in (curses.KEY_ENTER, ord("\n")):
        pass

# =============================================================================
# Main menu & application loop
# =============================================================================
import random

def draw_main_menu(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(0)
    opts = ["Play Built-In Levels", "Play Custom Levels",
            "Edit/Create Levels", "Exit"]
    idx = 0

    # Preload one random background for the session
    all_levels = [(None, lvl) for lvl in game_levels] + load_custom_levels()
    bg_name, bg_map = random.choice(all_levels)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # --- Draw dimmed background ---
        off_y = max((h - LEVEL_HEIGHT)//2, 0)
        off_x = max((w - LEVEL_WIDTH)//2, 0)
        for y, row in enumerate(bg_map):
            for x, ch in enumerate(row):
                stdscr.addch(off_y + y, off_x + x, ch, curses.A_DIM)

        # --- Overlay title & options ---
        # Vertical centering
        scores = load_scores()
        menu_height = 1 + len(opts) + (len(scores)+1 if scores else 0)
        start_y = (h - menu_height) // 2

        # Title
        title = "TerminalFormer"
        stdscr.addstr(start_y,
                      (w - len(title)) // 2,
                      title, curses.A_BOLD)

        # Options
        for i, opt in enumerate(opts):
            y = start_y + 1 + i
            x = (w - len(opt)) // 2
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(y, x, opt, attr)

        # Top scores
        if scores:
            sy = start_y + 1 + len(opts) + 1
            stdscr.addstr(sy,
                          (w - len("Top Times:")) // 2,
                          "Top Times:", curses.A_UNDERLINE)
            for i, s in enumerate(scores):
                line = f"{i+1}. {s:.2f}s"
                stdscr.addstr(sy + 1 + i,
                              (w - len(line)) // 2,
                              line)

        # No-custom-levels notice
        custom = load_custom_levels()
        if idx == 1 and not custom:
            note = "(no files in custom_levels/)"
            stdscr.addstr(start_y + 2,
                          (w - len(note)) // 2,
                          note, curses.A_DIM)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(opts) - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, ord("\n"), ord(" ")):
            return idx


def draw_custom_selection(stdscr):
    choices = load_custom_levels()
    if not choices:
        return None

    idx = 0
    n = len(choices)

    # Choose a random custom level for background
    bg_name, bg_map = random.choice(choices)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # --- Dimmed background of a custom level ---
        off_y = max((h - LEVEL_HEIGHT)//2, 0)
        off_x = max((w - LEVEL_WIDTH)//2, 0)
        for y, row in enumerate(bg_map):
            for x, ch in enumerate(row):
                stdscr.addch(off_y + y, off_x + x, ch, curses.A_DIM)

        # Center menu vertically
        menu_height = 1 + n
        start_y = (h - menu_height) // 2

        # Title
        title = "Select Custom Level (q=cancel)"
        stdscr.addstr(start_y,
                      (w - len(title)) // 2,
                      title, curses.A_BOLD)

        # Options
        for i, (fn, _) in enumerate(choices):
            y = start_y + 1 + i
            x = (w - len(fn)) // 2
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(y, x, fn, attr)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < n - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, ord("\n")):
            return choices[idx][1]
        elif key == ord("q"):
            return None

def main(stdscr):
    while True:
        choice = draw_main_menu(stdscr)

        if choice == 0:
            # Play built-in levels
            while True:
                timer = {"start": None}
                restart, leave = False, False
                for lvl in game_levels:
                    res = draw_game(stdscr, lvl, timer)
                    if res is None: restart = True; break
                    if res is False: leave = True; break
                if leave: break
                if restart: continue
                final = time.time() - timer["start"]
                save_score(final)
                draw_win(stdscr, final)
                break

        elif choice == 1:
            # Play a custom level
            custom = draw_custom_selection(stdscr)
            if not custom:
                continue
            while True:
                timer = {"start": None}
                res = draw_game(stdscr, custom, timer)
                if res is None: continue
                if res is False: break
                draw_win(stdscr, time.time() - timer["start"])
                break

        elif choice == 2:
            # Launch level editor
            level_editor_main(stdscr)

        else:
            # Exit
            break

if __name__ == "__main__":
    curses.wrapper(main)
