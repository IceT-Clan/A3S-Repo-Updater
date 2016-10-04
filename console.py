"""providing console actions"""
# Import Built-Ins
import sys
# Import Locals
import EscapeAnsi

class Output:
    """docstring for console"""
    def __init__(self, is_debug=False):
        super(Output, self).__init__()
        self.is_debug = is_debug
        self.ansi_escape = EscapeAnsi.EscapeAnsi()

    def printstatus(self, state, displayname="NO DISPLAY NAME", **kwargs):
        """print a status with information for the user"""
        state = str(state).lower()
        if state == "updating":
            # Updating
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_YELLOW
                             + "WAIT" + self.ansi_escape.RESET + " ] "
                             + "Updating " + displayname + "...")
        elif state == "is_up_to_date":
            # Is up to date
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_GREEN + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " is up to date" + "\n")
        elif state == "success_update":
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_GREEN + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " successfully updated" + "\n")
        elif state == "steambag_add":
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_BLUE + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " has been added to the Steam Bag" + "\n")
        elif state == "ace_opt_add":
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_BLUE + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " will be added to @ace_optinals" + "\n")
        elif state == "do_workshop":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_YELLOW + "WAIT"
                             + self.ansi_escape.RESET + " ] "
                             + "doing Steam Workshop..." + "\n")
        elif state == "linking":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_YELLOW + "WAIT"
                             + self.ansi_escape.RESET + " ] "
                             + "linking " + displayname + "...")
        elif state == "success_linking":
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_GREEN + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " successfully linked" + "\n")
        elif state == "is_linked":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_BLUE + "SKIP"
                             + self.ansi_escape.RESET + " ] " + displayname
                             + " is already linked" + "\n")
        elif state == "success_removed":
            sys.stdout.write("\r" + "[  " + self.ansi_escape.F_L_GREEN + "OK"
                             + self.ansi_escape.RESET + "  ] " + displayname
                             + " successfully removed" + "\n")
        elif state == "err_not_valid":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_RED + "FAIL"
                             + self.ansi_escape.RESET + " ] "
                             + kwargs["file_name"] + " is not a valid "
                             + kwargs["file_format"] + "\n")
        elif state == "err_not_exist":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_RED + "FAIL"
                             + self.ansi_escape.RESET + " ] " + displayname
                             + " does not exist" + "\n")
        elif state == "err_steam":
            sys.stdout.write("\r" + "[ " + self.ansi_escape.F_L_RED + "FAIL"
                             + self.ansi_escape.RESET + " ] "
                             + "Maybe SteamCMD did not download " + displayname
                             + "(" + kwargs["workshop_id"] + ") correctly? "
                             + "(use --steam-only to skip other sources)"
                             + "\n")
        else:
            raise TypeError(state + " is not a valid state")


    def debug(self, msg, add_newline=False):
        """print debug messages"""
        if add_newline:
            newline = "\n"
        else:
            newline = ""
        if self.is_debug:
            sys.stdout.write(newline + "[" + self.ansi_escape.BOLD + "DEBUG"
                             + self.ansi_escape.RESET + "] " + str(msg) + "\n")
