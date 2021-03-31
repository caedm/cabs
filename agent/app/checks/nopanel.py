#!/usr/bin/python2
from argparse import ArgumentParser
import os
from os.path import isfile
from subprocess import check_output, call

parser = ArgumentParser()
parser.add_argument('--debug', '-d', action='store_true')
args = parser.parse_args()

def win_info(user, display):
    if args.debug:
        template = ('0x01e00003 -1 0    {}  1024 24   rgsl-07 Top Expanded Edge Panel\n'
                    '0x01e00024 -1 0    1536 1024 24   rgsl-07 Bottom Expanded Edge Panel\n')
        return template.format('-48' if isfile('/tmp/no_panel') else '0')
    else:
        return check_output("script -c 'DISPLAY={} sudo -u {} wmctrl -lG' /dev/null"
                            "| { grep -v Script || true; }".format(display, user), shell=True)

def panel_check():
    no_panel = isfile('/tmp/cabs-nopanel')
    graphical_users = [line.split() for line in check_output("who").split('\n')
                                    if " :0" in line]
    if graphical_users:
        user = graphical_users[0][0]
        display = graphical_users[0][1]
        info = win_info(user, display).split('\n')
        y_coords = [line.split()[3] for line in info if "Top Expanded Edge Panel" in line]
        no_panel = any(int(coord) < 0 for coord in y_coords)

        # We can only check if there's a panel when someone is logged in. If the
        # user logs out, we want to remember that there wasn't a panel.
        if no_panel:
            open('/tmp/cabs-nopanel', 'a').close()
        else:
            try:
                os.remove('/tmp/cabs-nopanel')
            except OSError:
                pass

    elif no_panel and int(check_output('who | wc -l', shell=True)) == 0:
        call('shutdown -r now'.split())

    return "no_panel" if no_panel else "Okay"

print panel_check()
