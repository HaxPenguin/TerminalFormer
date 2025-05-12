import curses
import os

LEVEL_WIDTH   = 80
LEVEL_HEIGHT  = 11
BLOCK_CHAR    = "▒"
EMPTY_CHAR    = " "
SAVE_FOLDER   = "custom_levels"

def save_level(level_data, filename):
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    with open(os.path.join(SAVE_FOLDER, filename), "w") as f:
        for row in level_data:
            f.write("".join(row).rstrip() + "\n")

def load_level(filename):
    path = os.path.join(SAVE_FOLDER, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        lines = f.readlines()
    return [
        list(line.rstrip("\n").ljust(LEVEL_WIDTH, EMPTY_CHAR)[:LEVEL_WIDTH])
        for line in lines[:LEVEL_HEIGHT]
    ]

def list_levels():
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    return [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".txt")]

def center_coords(term_h, term_w, content_h, content_w):
    y = max((term_h - content_h)//2, 0)
    x = max((term_w - content_w)//2, 0)
    return y, x

def level_editor(stdscr, level, filename=None):
    curses.curs_set(1)
    stdscr.keypad(True)
    y, x = 0, 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        start_y, start_x = center_coords(h, w, LEVEL_HEIGHT + 5, LEVEL_WIDTH)

        # draw background
        for ry in range(h):
            for cx in range(w):
                try:
                    stdscr.addstr(ry, cx, EMPTY_CHAR)
                except curses.error:
                    pass

        # draw level
        for ry, row in enumerate(level):
            stdscr.addstr(start_y + ry, start_x, "".join(row))

        stdscr.addstr(start_y + LEVEL_HEIGHT + 1, start_x,
                      "(Arrows to move, Space to toggle, 's' to save, 'q' to quit)")
        stdscr.move(start_y + y, start_x + x)
        stdscr.refresh()

        key = stdscr.getch()
        if   key == curses.KEY_UP    and y > 0:               y -= 1
        elif key == curses.KEY_DOWN  and y < LEVEL_HEIGHT-1:  y += 1
        elif key == curses.KEY_LEFT  and x > 0:               x -= 1
        elif key == curses.KEY_RIGHT and x < LEVEL_WIDTH-1:   x += 1
        elif key == ord(' '):
            # Prevent toggling the floor row
            if y < LEVEL_HEIGHT - 1:
                level[y][x] = BLOCK_CHAR if level[y][x] == EMPTY_CHAR else EMPTY_CHAR
        elif key == ord('s'):
            if filename is None:
                stdscr.addstr(start_y + LEVEL_HEIGHT + 2, start_x, "Enter filename: ")
                curses.echo()
                name = stdscr.getstr(start_y + LEVEL_HEIGHT + 2,
                                     start_x + 16, 20).decode("utf-8").strip()
                curses.noecho()
                filename = name + ".txt"
            save_level(level, filename)
            stdscr.addstr(start_y + LEVEL_HEIGHT + 3, start_x, f"Saved as {filename}")
            stdscr.refresh()
            stdscr.getch()
            break
        elif key == ord('q'):
            break

def select_existing_level(stdscr):
    levels = list_levels()
    if not levels:
        return None
    idx = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        header = "Select a level to edit (Enter to load, q to cancel):"
        content_h = len(levels) + 4
        content_w = max(len(header), max(len(l) for l in levels) + 4)
        start_y, start_x = center_coords(h, w, content_h, content_w)

        stdscr.addstr(start_y, start_x, header)
        for i, name in enumerate(levels):
            mode = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(start_y + 2 + i, start_x + 2, name, mode)
        stdscr.refresh()

        key = stdscr.getch()
        if   key == curses.KEY_UP   and idx > 0:            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(levels)-1: idx += 1
        elif key in (curses.KEY_ENTER, ord("\n")):          return levels[idx]
        elif key == ord('q'):                              return None

def main_menu(stdscr):
    opts = ["Make a New Level", "Edit Existing Level", "Exit"]
    cur = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "TerminalFormer Level Editor"
        start_y, start_x = center_coords(h, w, len(opts)+4, len(title)+4)

        stdscr.addstr(start_y, start_x, title)
        for i, o in enumerate(opts):
            mode = curses.A_REVERSE if i == cur else curses.A_NORMAL
            stdscr.addstr(start_y + 2 + i, start_x + 4, o, mode)
        stdscr.refresh()

        k = stdscr.getch()
        if   k == curses.KEY_UP   and cur > 0:        cur -= 1
        elif k == curses.KEY_DOWN and cur < len(opts)-1: cur += 1
        elif k in (curses.KEY_ENTER, ord("\n")):      return opts[cur]

def editor_main(stdscr):
    while True:
        choice = main_menu(stdscr)
        if choice == "Make a New Level":
            # New level: empty rows + solid floor
            level = [
                [EMPTY_CHAR]*LEVEL_WIDTH
                for _ in range(LEVEL_HEIGHT-1)
            ] + [
                [BLOCK_CHAR]*LEVEL_WIDTH
            ]
            level_editor(stdscr, level)
        elif choice == "Edit Existing Level":
            sel = select_existing_level(stdscr)
            if sel:
                lvl = load_level(sel)
                if lvl:
                    level_editor(stdscr, lvl, sel)
        else:  # Exit
            break

if __name__ == "__main__":
    curses.wrapper(editor_main)
