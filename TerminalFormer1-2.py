import curses
import time
import os

# Constants
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

# Built-in levels
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

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE) as f:
        return [float(line.strip()) for line in f if line.strip()]

def save_score(new_time):
    scores = sorted(load_scores() + [new_time])[:MAX_SCORES]
    with open(SCORE_FILE, "w") as f:
        f.writelines(f"{s:.2f}\n" for s in scores)

def load_custom_levels():
    levels = []
    if not os.path.isdir(CUSTOM_FOLDER):
        return levels
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

def select_custom_level(stdscr):
    choices = load_custom_levels()
    if not choices:
        return None
    idx = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        start_y = (h - len(choices) - 2)//2
        stdscr.addstr(start_y, (w - 35)//2,
                      "Select Custom Level (Enter=play, q=cancel)", curses.A_BOLD)
        for i, (fn, _) in enumerate(choices):
            stdscr.addstr(start_y+2+i, (w-len(fn))//2,
                          fn, curses.A_REVERSE if i==idx else curses.A_NORMAL)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and idx>0: idx-=1
        elif key == curses.KEY_DOWN and idx<len(choices)-1: idx+=1
        elif key in (curses.KEY_ENTER, ord("\n")): return choices[idx][1]
        elif key == ord("q"): return None

def draw_menu(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(0)
    opts = ["Play Built-In Levels", "Play Custom Levels", "Exit"]
    idx = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        scores = load_scores()
        custom = load_custom_levels()
        start_y = (h - len(opts) - (len(scores)+3 if scores else 0))//2
        stdscr.addstr(start_y, (w-14)//2, "TerminalFormer", curses.A_BOLD)
        for i,o in enumerate(opts):
            stdscr.addstr(start_y+2+i, (w-len(o))//2,
                          o, curses.A_REVERSE if i==idx else curses.A_NORMAL)
        if scores:
            sy = start_y+2+len(opts)+1
            stdscr.addstr(sy, (w-9)//2, "Top Times:", curses.A_UNDERLINE)
            for i,s in enumerate(scores):
                stdscr.addstr(sy+1+i, (w-10)//2, f"{i+1}. {s:.2f}s")
        if idx==1 and not custom:
            stdscr.addstr(start_y+3, (w-27)//2,
                          "(no files in custom_levels/)", curses.A_DIM)
        stdscr.refresh()
        key = stdscr.getch()
        if key==curses.KEY_UP and idx>0: idx-=1
        elif key==curses.KEY_DOWN and idx<len(opts)-1: idx+=1
        elif key in (curses.KEY_ENTER, ord("\n"), ord(" ")): return idx

def draw_game(stdscr, level_map, timer):
    # pad to rectangle
    level_map = [r.ljust(LEVEL_WIDTH, EMPTY_CHAR)[:LEVEL_WIDTH] for r in level_map]
    curses.curs_set(0); stdscr.nodelay(1); stdscr.timeout(1000//FPS)
    H,W = LEVEL_HEIGHT, LEVEL_WIDTH
    win_h,win_w = stdscr.getmaxyx()
    off_y,off_x = max((win_h-H)//2,0), max((win_w-W)//2,0)
    px,py,vy = 2,H-2,0; on_ground=False

    while True:
        stdscr.clear()
        for y,row in enumerate(level_map):
            stdscr.addstr(off_y+y, off_x, row)
        elapsed = time.time() - timer.get("start",0) if timer.get("start") else 0.0
        stdscr.addstr(0, win_w-13, f"Time: {elapsed:05.2f}s")
        key = stdscr.getch()

        if key == ord("l"):
            # Leave level, return to menu without recording time
            return False

        if key == ord("r"):
            # Restart level
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

        if vy > 0:
            for ytest in range(py + 1, int(new_py) + 1):
                if level_map[min(ytest, H-1)][px] in "▒#":
                    new_py, vy, on_ground = ytest - 1, 0, True
                    break
        elif vy < 0:
            for ytest in range(py - 1, int(new_py) - 1, -1):
                if level_map[max(ytest,0)][px] in "▒#":
                    new_py, vy = ytest + 1, 0
                    break

        py = max(0, min(H-1, int(new_py)))

        if move_left:
            for _ in range(MOVE_SPEED):
                if px > 0 and level_map[py][px-1] not in "▒#":
                    px -= 1
                else:
                    break
        if move_right:
            for _ in range(MOVE_SPEED):
                if px+1 < W and level_map[py][px+1] not in "▒#":
                    px += 1
                else:
                    break

        stdscr.addch(off_y+py, off_x+px, "#")
        stdscr.refresh()
        time.sleep(1/FPS)

        if px >= W-1:
            # Level completed
            return True

def draw_win(stdscr, final_time):
    curses.curs_set(0); stdscr.nodelay(0); stdscr.clear()
    h,w = stdscr.getmaxyx()
    msgs = ["You Win!", f"Final time: {final_time:05.2f}s", "Press Enter to exit"]
    for i,m in enumerate(msgs):
        stdscr.addstr((h-len(msgs))//2+i, (w-len(m))//2, m,
                      curses.A_BOLD if i==0 else curses.A_NORMAL)
    stdscr.refresh(); curses.flushinp()
    while stdscr.getch() not in (curses.KEY_ENTER, ord("\n")):
        pass

def main(stdscr):
    while True:
        choice = draw_menu(stdscr)

        if choice == 0:
            # Play built-in levels
            while True:
                timer = {"start": None}
                restart_flag = False
                leave_flag   = False

                for lvl in game_levels:
                    result = draw_game(stdscr, lvl, timer)
                    if result is None:      # pressed 'r'
                        restart_flag = True
                        break
                    if result is False:     # pressed 'l'
                        leave_flag = True
                        break
                    # else result == True -> level completed, continue to next

                if leave_flag:
                    # Leave to main menu
                    break
                if restart_flag:
                    # Restart from first built-in level
                    continue

                # Completed all levels
                final = time.time() - timer["start"]
                save_score(final)
                draw_win(stdscr, final)
                break  # back to menu

        elif choice == 1:
            # Play a custom level
            custom = select_custom_level(stdscr)
            if not custom:
                continue  # back to menu

            while True:
                timer = {"start": None}
                result = draw_game(stdscr, custom, timer)
                if result is None:   # 'r' pressed
                    continue           # restart same custom level
                if result is False:  # 'l' pressed
                    break              # back to menu
                # Completed custom level
                draw_win(stdscr, time.time() - timer["start"])
                break

        else:
            # Exit
            break


if __name__ == "__main__":
    curses.wrapper(main)
