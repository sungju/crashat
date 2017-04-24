#!/usr/bin/env python

import curses
import os

class PyWindow:
    KEY_LEFT_PRESSED = 0x100000
    KEY_RIGHT_PRESSED = 0x200000
    KEY_ESCAPE_PRESSED = 0x300000
    stdscr = 0

    def __init__(self):
        try:
            os.environ['ESCDELAY']
        except KeyError:
            os.environ['ESCDELAY'] = '25'

    def init_winlib(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)


    def exit_winlib(self):
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


    def clear_box(self, screen, x, y, width, height, color = 0):
        (maxy, maxx) = screen.getmaxyx()
        maxy = maxy - 1
        maxx = maxx - 1
        if (x > maxx):
            x = maxx
        if (x + width - 1 > maxx):
            width = maxx - x - 1

        if (y > maxy):
            y = maxy
        if (y + height - 1 > maxy):
            height = maxy - y - 1

        for x1 in range(0, width):
            for y1 in range(0, height):
                screen.addch(y + y1, x + x1, ' ',
                            color | curses.A_REVERSE)


    def draw_box(self, screen, x, y, width, height, color = 0):
        (maxy, maxx) = screen.getmaxyx()
        maxy = maxy - 1
        maxx = maxx - 1
        if (x > maxx):
            x = maxx
        if (x + width - 1 > maxx):
            width = maxx - x

        if (y > maxy):
            y = maxy
        if (y + height - 1 > maxy):
            height = maxy - y

        screen.addch(y, x, '+', color)
        screen.addch(y + height - 1, x, '+', color)
        screen.addch(y, x + width - 1, '+', color)
        screen.addch(y + height - 1, x + width - 1, '+', color)

        for x1 in range(1, width - 1):
            screen.addch(y, x + x1, '-', color)
            screen.addch(y + height - 1, x + x1, '-', color)

        for y1 in range(1, height - 1):
            screen.addch(y + y1, x, '|', color)
            screen.addch(y + y1, x + width - 1, '|', color)

    def fill_box(self, screen, x, y, width, height, color = 0):
        self.clear_box(screen, x, y, width, height, color)
        self.draw_box(screen, x, y, width, height, color | curses.A_REVERSE)


    def hmenu(self, screen, x, y, width, menu_list,
            selected_color = 3, normal_color = 5,
            vertical_keys = False, selected_item = 0):
        if (width == -1):
            for item in menu_list:
                if (len(item) > width):
                    width = len(item)

        (maxy, maxx) = screen.getmaxyx()
        if (x > maxx or y > maxy):
            return -1
        if (y + len(menu_list) > maxy):
            return -2

        if (x + width > maxx):
            width = maxx - x

        count = 0
        selected_color = selected_color | curses.A_REVERSE
        normal_color = normal_color | curses.A_REVERSE
        for item in menu_list:
            menu_list[count] = item.ljust(width)[:width]
            screen.addstr(y + count, x, menu_list[count], normal_color)
            count = count + 1

        expand_key = 0
        screen.addstr(y + selected_item, x, menu_list[selected_item],
                    selected_color)
        while True:
            c = screen.getch()
            screen.addstr(y + selected_item, x,
                        menu_list[selected_item], normal_color)
            if (c == curses.KEY_UP):
                selected_item = selected_item - 1
                if (selected_item < 0):
                    selected_item = len(menu_list) - 1
            elif (c == curses.KEY_DOWN):
                selected_item = (selected_item + 1) % len(menu_list)
            elif (vertical_keys == True and c == curses.KEY_LEFT):
                expand_key = self.KEY_LEFT_PRESSED
                break
            elif (vertical_keys == True and c == curses.KEY_RIGHT):
                expand_key = self.KEY_RIGHT_PRESSED
                break
            elif (c == 27):
                expand_key = self.KEY_ESCAPE_PRESSED
                break
            elif (c == curses.KEY_ENTER or c == 10 or c == 13):
                break

            screen.addstr(y + selected_item, x,
                        menu_list[selected_item], selected_color)

        screen.addstr(y + selected_item, x,
                    menu_list[selected_item], selected_color)

        return selected_item + expand_key


    def hmenu_window(self, screen, x, y, width, menu_list,
                     selected_color = 3, normal_color = 5,
                     vertical_keys = False,
                     restore_background = False,
                     selected_item = 0):
        if (width == -1):
            max_width = 0
            for item in menu_list:
                if (len(item) > max_width):
                    max_width = len(item)
            width = max_width + 2

        if restore_background == True:
            saved_data = self.save_window(screen, x, y,
                                          x + width, y + len(menu_list) + 1)
        self.fill_box(screen, x, y, width, len(menu_list) + 2,
                normal_color)
        selected_item = self.hmenu(screen, x + 1, y + 1, width - 2, menu_list,
                          selected_color, normal_color,
                          vertical_keys, selected_item)
        if restore_background == True:
            self.restore_window(screen, x, y, saved_data)

        return selected_item


    def vmenu(self, screen, x, y, width, menu_list,
              selected_color = 3, normal_color = 5,
              draw_bar = False, center = True, down_key = False,
              selected_item = 0, pressed_key = 0):
        (maxy, maxx) = screen.getmaxyx()
        if (x > maxx or y > maxy):
            return -1

        if (x + width > maxx):
            width = maxx - x

        selected_color = selected_color | curses.A_REVERSE
        normal_color = normal_color | curses.A_REVERSE

        xpos = 0
        menu_pos = []
        for item in menu_list:
            menu_pos.append(xpos)
            xpos = xpos + len(item) + 2

        if (x + xpos - 2 > maxx):
            return -2

        if (draw_bar == True):
            screen.addstr(y, x, " ".ljust(width)[:width], normal_color)

        if (center == True):
            x = x + width / 2 - (xpos - 2) / 2

        count = 0
        for item in menu_list:
            screen.addstr(y, x + menu_pos[count], item, normal_color)
            count = count + 1

        screen.addstr(y, x + menu_pos[selected_item],
                      menu_list[selected_item], selected_color)
        max_item = len(menu_list)
        while True:
            if (pressed_key == 0 or pressed_key == self.KEY_ESCAPE_PRESSED):
                c = screen.getch()
            elif pressed_key == self.KEY_LEFT_PRESSED:
                c = curses.KEY_LEFT
            elif pressed_key == self.KEY_RIGHT_PRESSED:
                c = curses.KEY_RIGHT

            screen.addstr(y, x + menu_pos[selected_item],
                        menu_list[selected_item], normal_color)

            if c == curses.KEY_LEFT:
                selected_item = selected_item - 1
                if (selected_item < 0):
                    selected_item = max_item - 1
            elif c == curses.KEY_RIGHT:
                selected_item = (selected_item + 1) % max_item
            elif c == 27:
                return self.KEY_ESCAPE_PRESSED
            elif c == curses.KEY_DOWN and down_key != False:
                break
            elif c == curses.KEY_ENTER or c == 10 or c == 13:
                break

            screen.addstr(y, x + menu_pos[selected_item],
                        menu_list[selected_item], selected_color)

            if (pressed_key != 0):
                break

        screen.addstr(y, x + menu_pos[selected_item],
                    menu_list[selected_item], selected_color)
        return selected_item


    def dialog_msg(self, screen, x, y, width, height, color,
                title, msg, menu_list):
        saved_data = self.save_window(screen, x, y, width, height)

        self.fill_box(screen, x, y, width, height, color)
        screen.addstr(y, x + width / 2 - len(title) / 2,
                    title, color | curses.A_REVERSE)
        msg_list = msg.split('\n')
        count = 1
        for msg_str in msg_list:
            screen.addstr(y + count, x + width / 2 - len(msg_str) / 2,
                        msg_str, color | curses.A_REVERSE)
            count = count + 1

        selected_item = self.vmenu(screen, x + 1, y + 3, width - 2, menu_list,
                            curses.color_pair(10), curses.color_pair(8))
        self.restore_window(screen, x, y, saved_data)

        return selected_item


    def save_window(self, screen, x, y, width, height):
        saved_data = []
        for ypos in range(0, height):
            saved_row = []
            for xpos in range(0, width):
                saved_row.append(screen.inch(y + ypos, x + xpos))
            saved_data.append(saved_row)

        return saved_data


    def restore_window(self, screen, x, y, saved_data):
        ypos = 0
        for row in saved_data:
            xpos = 0
            for column in row:
                screen.delch(y + ypos, x + xpos)
                screen.insch(y + ypos, x + xpos, column)
                xpos = xpos + 1
            ypos = ypos + 1


    def text_window(self, screen, x, y, width, height, xpos, ypos,
                    string_list, text_color=5):
        for i in range(0, height):
            text_pos = ypos + i
            if (text_pos >= len(string_list)):
                text_msg = ""
            else:
                text_msg = string_list[text_pos]
                if (len(text_msg) < xpos):
                    text_msg = ""
                else:
                    text_msg = text_msg[xpos:]

            text_msg = text_msg.ljust(width)[:width]
            screen.addstr(y + i, x, text_msg, text_color)


    def text_viewer(self, screen, x, y, width, height,
                    string_list, text_color=5, show_scroll=True):
        saved_data = self.save_window(screen, x, y, width, height)
        self.fill_box(screen, x, y, width, height, text_color)
        t_x = x + 1
        t_y= y + 1
        t_width = width - 2
        t_height = height - 2
        xpos = ypos = 0
        max_width = width
        for i in string_list:
            if len(i) > max_width:
                max_width = len(i)
        x_percent = y_percent = 0

        max_width = max_width - 1
        x_scale = float(max_width) / (t_width - 1)
        y_scale = float(len(string_list)) / (t_height - 1)
        if x_scale == 0.0:
            x_scale = 1.0
        if y_scale == 0.0:
            y_scale = 1.0

        while True:
            screen.addch(y + height - 1, x + x_percent + 1,
                         '-', text_color)
            screen.addch(y + y_percent + 1, x + width - 1,
                         '|', text_color)
            self.text_window(screen, t_x, t_y, t_width, t_height,
                        xpos, ypos, string_list, text_color)
            x_percent = int(xpos / x_scale)
            y_percent = int(ypos / y_scale)
            screen.addch(y + height - 1, x + x_percent + 1,
                         '#', text_color)
            screen.addch(y + y_percent + 1, x + width - 1,
                         '#', text_color)
            ch = screen.getch()
            if ch == curses.KEY_UP:
                ypos = ypos - 1
                if ypos < 0:
                    ypos = 0
            elif ch == curses.KEY_DOWN:
                ypos = ypos + 1
                if ypos >= len(string_list):
                    ypos = len(string_list) - 1
            elif ch == curses.KEY_LEFT:
                xpos = xpos - 1
                if xpos < 0:
                    xpos = 0
            elif ch == curses.KEY_RIGHT:
                xpos = xpos + 1
                if xpos >= max_width:
                    xpos = max_width
            elif ch == 27:
                break

        self.restore_window(screen, x, y, saved_data)


    def pulldown_menu(self, screen, x, y, maxx, vmenu_list, hmenu_list,
                      selected_color = 3, normal_color = 5,
                      restore_window = True):
        if restore_window == True:
            saved_data = self.save_window(screen, x, y, maxx, 1)

        selected_vmenu = 2
        selected_hmenu = 0
        x_pos_list = []
        xpos = x
        hmenu_selected = []
        for item in vmenu_list:
            x_pos_list.append(xpos)
            xpos = xpos + len(item) + 2
            hmenu_selected.append(0)

        while (True):
            selected_vmenu = self.vmenu(screen, x, y, maxx, vmenu_list,
                                        selected_color, normal_color,
                                        True, False, True,
                                        selected_vmenu, selected_hmenu)

            if (selected_vmenu == -1 or
                selected_vmenu == self.KEY_ESCAPE_PRESSED):
                break

            selected_hmenu = self.hmenu_window(screen,
                                               x_pos_list[selected_vmenu],
                                               y + 1, -1,
                                               hmenu_list[selected_vmenu],
                                               selected_color, normal_color,
                                               True, True,
                                               hmenu_selected[selected_vmenu])
            if ((selected_hmenu & self.KEY_ESCAPE_PRESSED)
                == self.KEY_ESCAPE_PRESSED):
                hmenu_selected[selected_vmenu] = selected_hmenu & ~self.KEY_ESCAPE_PRESSED
                selected_hmenu = 0
                continue
            elif ((selected_hmenu & self.KEY_LEFT_PRESSED)
                  == self.KEY_LEFT_PRESSED):
                hmenu_selected[selected_vmenu] = selected_hmenu & ~self.KEY_LEFT_PRESSED
                selected_hmenu = self.KEY_LEFT_PRESSED
                continue
            elif ((selected_hmenu & self.KEY_RIGHT_PRESSED)
                  == self.KEY_RIGHT_PRESSED):
                hmenu_selected[selected_vmenu] = selected_hmenu & ~self.KEY_RIGHT_PRESSED
                selected_hmenu = self.KEY_RIGHT_PRESSED
                continue
            else:
                break

            hmenu_selected[selected_vmenu] = selected_hmenu

        if restore_window == True:
            self.restore_window(screen, x, y, saved_data)


def unit_test():
    mywin = PyWindow()
    mywin.init_winlib()
    (maxy, maxx) = mywin.stdscr.getmaxyx()
    """
    mywin.clear_box(stdscr, 0, 0, 3, 3, curses.color_pair(7))
    mywin.draw_box(stdscr, 0, 0, 3, 3,
                   curses.color_pair(7) | curses.A_REVERSE)
    mywin.clear_box(stdscr, 13, 10, 11, 11, curses.color_pair(5))
    mywin.draw_box(stdscr, 13, 10, 11, 11, curses.color_pair(5))
    mywin.clear_box(stdscr, 5, 8, 15, 10, curses.color_pair(3))
    mywin.draw_box(stdscr, 5, 8, 15, 10,
             curses.color_pair(3) | curses.A_REVERSE | curses.A_BLINK)
    mywin.clear_box(stdscr, 25, 12, 8, 5, curses.color_pair(10))
    mywin.draw_box(stdscr, 25, 12, 8, 5,
                   curses.color_pair(10) | curses.A_REVERSE)

    mywin.fill_box(stdscr, 80, 5, 30, 15, curses.color_pair(15))

    saved_data = mywin.save_window(stdscr, 15, 10, 30, 5)
    result = mywin.dialog_msg(stdscr, 15, 10, 30, 5, curses.color_pair(4),
                        "< Warning >", "Be careful\nwhat you are doing",
                        ["[ Yes ]", "[ No ]", "[ Cancel ]"])
    mywin.restore_window(stdscr, 15, 10, saved_data)

    mywin.vmenu(stdscr, 0, 0, maxx,
          ["File", "Edit", "View", "Themes", "Window", "Favorites"],
          curses.color_pair(3), curses.color_pair(5),
          True, False)
    saved_data = mywin.save_window(stdscr, 10, 1, 34, 8)
    mywin.hmenu_window(stdscr, 10, 1, 34,
          ["First", "Second", "Thrid", "Fourth", "Fifth", "Sixth"],
          curses.color_pair(3), curses.color_pair(5))
    mywin.restore_window(stdscr, 10, 1, saved_data)

    mywin.fill_box(stdscr, 4, 4, 52, 7, curses.color_pair(25))
    for i in range(0, 5):
        mywin.text_window(stdscr, 5, 5, 50, 5, 0, i,
                    ["Hello",
                     "This is Daniel Kwon",
                     "",
                     "I'm working as a support engineer",
                     "Good to see you"],
                    curses.color_pair(25) | curses.A_REVERSE)

        c = stdscr.getch()
"""

    mywin.text_viewer(mywin.stdscr, 15, 8, 20, 8,
                ["Hello",
                "This is Sungju Kwon",
                "",
                "I'm a software engineer.",
                "Good to see you"],
                curses.color_pair(25) | curses.A_REVERSE)

    hmenu_list = ["File", "Edit", "View", "Help"]
    vmenu_list = [["New", "Open   ", "Save", "Close", "Quit"],
                  ["Copy", "Cut", "Paste   "],
                  ["View single", "View multiple   ", "Full Screen"],
                  ["About", "Help Online "]]
    mywin.pulldown_menu(mywin.stdscr, 0, 0, maxx, hmenu_list, vmenu_list,
                        curses.color_pair(3), curses.color_pair(5),
                        True)

    c = mywin.stdscr.getch()
    mywin.exit_winlib()


if __name__ == "__main__":
    unit_test()
