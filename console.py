class console:
    """docstring for console"""
    def __init__(self, is_debug=False):
        super(console, self).__init__()
        self.is_debug = is_debug

    def printstatus(state, displayname="NO DISPLAY NAME", **kwargs):
        """print a status with information for the user"""
        state = state.lower();
        if state == "update":
            # Updating
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_YELLOW + "WAIT" +
                             ansi_escape.RESET + " ] " + "Updating " +
                             displayname + "...")
        elif state == 1:
            # Is up to date
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " + displayname +
                             " is up to date" + "\n")
        elif state == 2:
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_GREEN + "OK" +
                             ansi_escape.RESET + "  ] " + displayname +
                             " successfully updated" + "\n")
        elif state == 3:
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_BLUE + "OK" +
                             ansi_escape.RESET + "  ] " + displayname +
                             " has been added to the Steam Bag" + "\n")
        elif state == 4:
            sys.stdout.write("\r" + "[  " + ansi_escape.F_L_BLUE + "OK" +
                             ansi_escape.RESET + "  ] " + displayname +
                             " will be added to @ace_optinals" + "\n")
        elif state == 5:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_YELLOW + "WAIT" +
                             ansi_escape.RESET + " ] " +
                             "doing Steam Workshop" + "\n")
        elif state == 6:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_BLUE + "SKIP" +
                             ansi_escape.RESET + " ] " + displayname +
                             " is already linked" + "\n")
        elif state == -1:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " + displayname +
                             " is not a valid ZIP-Archive" + "\n")
        elif state == -2:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " + displayname +
                             " does not exist" + "\n")
        elif state == -3:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " +
                             "Maybe SteamCMD did not download " + displayname +
                             " correctly? " +
                             "(use --steam-only to skip other sources)" + "\n")
        elif state == -4:
            sys.stdout.write("\r" + "[ " + ansi_escape.F_L_RED + "FAIL" +
                             ansi_escape.RESET + " ] " + displayname +
                             " is not a valid RAR-Archive" + "\n")

    def debug(msg, add_newline=False):
        """print debug messages"""
        if add_newline:
            newline = "\n"
        else:
            newline = ""
        if is_debug:
            sys.stdout.write(newline + "[" + ansi_escape.BOLD + "DEBUG" +
                             ansi_escape.RESET + "] " + str(msg) + "\n")
