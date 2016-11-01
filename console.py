"""providing console actions"""
# Import Built-Ins
import sys
# Import Locals
from EscapeAnsi import EscapeAnsi as ansi_escape


class Output:
    """docstring for console"""
    def __init__(self, is_debug=False):
        super(Output, self).__init__()
        self.is_debug = is_debug

    def printerrstate(self, state, args):
        """print a error status with information for the user"""
        if state == "err_not_valid":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " +
                             args[0] + " is not a valid " +
                             args[1] + "\n")
        elif state == "err_not_exist":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " +
                             args[0] +
                             " does not exist" + "\n")
        elif state == "err_steam":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " +
                             "Maybe SteamCMD did not download " +
                             args[0] +
                             "(" + args[1] + ") correctly? " +
                             "(use --steam-only to skip other sources)" +
                             "\n")
        elif state == "err_skip":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "SKIP" +
                             ansi_escape.RESET + " ] " +
                             "Error updating " + displayname + "\n")
        else:
            raise TypeError(state + " is not a valid state")

    def printstatus(self, state, *args):
        """print a status with information for the user"""
        state = str(state).lower()
        if state == "updating":
            # Updating
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_YELLOW +
                             "WAIT" + ansi_escape.RESET + " ] " +
                             "Updating " + args[0] + "...")
        elif state == "is_up_to_date":
            # Is up to date
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] + " is up to date" + "\n")
        elif state == "success_update":
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] +
                             " successfully updated" + "\n")
        elif state == "steambag_add":
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_BLUE + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] +
                             " has been added to the Steam Bag" + "\n")
        elif state == "ace_opt_add":
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_BLUE + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] +
                             " will be added to @ace_optinals" + "\n")
        elif state == "do_workshop":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_YELLOW +
                             "WAIT" + ansi_escape.RESET + " ] " +
                             "doing Steam Workshop..." + "\n")
        elif state == "linking":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_YELLOW +
                             "WAIT" + ansi_escape.RESET + " ] "
                             "linking " + args[0] + "...")
        elif state == "success_linking":
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] +
                             " successfully linked" + "\n")
        elif state == "is_linked":
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_BLUE + "SKIP" +
                             ansi_escape.RESET + " ] " +
                             args[0] +
                             " is already linked" + "\n")
        elif state == "success_removed":
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " +
                             args[0] +
                             " successfully removed" + "\n")
        elif state.startswith("err"):
            self.printerrstate(state, args)
        else:
            raise TypeError(state + " is not a valid state")

    def debug(self, msg, add_newline=False):
        """print debug messages"""
        if add_newline:
            newline = "\n"
        else:
            newline = ""
        if self.is_debug:
            sys.stdout.write(newline + "[" + ansi_escape.BOLD + "DEBUG" +
                             ansi_escape.RESET + "] " + str(msg) + "\n")
