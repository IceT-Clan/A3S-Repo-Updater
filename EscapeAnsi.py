"""providing EscapeAnsi"""


class EscapeAnsi:
    """http://misc.flogisoft.com/bash/tip_colors_and_formatting
       ANSI/VT100 colors and formats
       http://ascii-table.com/ansi-escape-sequences.php"""

    # formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    STANDOUT = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    FORMAT_6 = '\033[6m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'

    RESET = '\033[m'

    BOLD_OFF = '\033[21m'
    DIM_OFF = '\033[22m'
    STANDOUT_OFF = '\033[23m'
    UNDERLINE_OFF = '\033[24m'
    BLINK_OFF = '\033[25m'
    FORMAT_6_OFF = '\033[26m'
    REVERSE_OFF = '\033[27m'
    HIDDEN_OFF = '\033[28m'

    # 8 foreground colors
    F_COLOR_OFF = '\033[39m'
    F_BLACK = '\033[30m'
    F_RED = '\033[31m'
    F_GREEN = '\033[32m'
    F_YELLOW = '\033[33m'
    F_BLUE = '\033[34m'
    F_MAGENTA = '\033[35m'
    F_CYAN = '\033[36m'

    F_L_GRAY = '\033[37m'
    F_GRAY = '\033[90m'

    F_L_RED = '\033[91m'
    F_L_GREEN = '\033[92m'
    F_L_YELLOW = '\033[93m'
    F_L_BLUE = '\033[94m'
    F_L_MAGENTA = '\033[95m'
    F_L_CYAN = '\033[96m'

    F_WHITE = '\033[97m'

    # 8 background colors
    B_COLOR_OFF = '\033[49m'
    B_BLACK = '\033[40m'
    B_RED = '\033[41m'
    B_GREEN = '\033[42m'
    B_YELLOW = '\033[43m'
    B_BLUE = '\033[44m'
    B_MAGENTA = '\033[45m'
    B_CYAN = '\033[46m'

    B_L_GRAY = '\033[47m'
    B_GRAY = '\033[100m'

    B_L_RED = '\033[101m'
    B_L_GREEN = '\033[102m'
    B_L_YELLOW = '\033[103m'
    B_L_BLUE = '\033[104m'
    B_L_MAGENTA = '\033[105m'
    B_L_CYAN = '\033[106m'

    B_WHITE = '\033[107m'

    F_COLOR_INIT = '\033[38;5;'
    B_COLOR_INIT = '\033[48;5;'

    ERASE_DISPLAY = '\033[2J'
    ERASE_LINE = '\033[K'

    # 256 foreground colors
    def f_color(self, color_number):
        """print foreground color switch"""
        return ''.join([self.F_COLOR_INIT, color_number, 'm'])

    # 256 background colors
    def b_color(self, color_number):
        """print background color switch"""
        return ''.join([self.B_COLOR_INIT, color_number, 'm'])

    def cursor_up(lines):
        """print cursor up"""
        return ''.join(['\033[', lines, 'A'])

    def cursor_down(lines):
        """print cursor down"""
        return ''.join([['\033[', lines, 'B']])

    def cursor_left(columns):
        """print cursor left"""
        return ''.join([['\033[', columns, 'C']])

    def cursor_right(columns):
        """print cursor right"""
        return ''.join([['\033[', columns, 'D']])

    def set_cursor(line, column, alternative=False):
        """print set cursor"""
        if not alternative:
            return ''.join([['\033[', line, ';', column, 'H']])
        return ''.join([['\033[', line, ';', column, 'f']])

