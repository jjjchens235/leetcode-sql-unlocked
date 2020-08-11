import argparse
import time

class HelpMenu:
    '''
    Using argparse library for unintended purpose- to format help menu
    '''
    def __init__(self, default_num_to_display):
        #setting max_help_positioin to keep keyword and help description on same line
        formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=40)
        parser = argparse.ArgumentParser(formatter_class = formatter, usage=argparse.SUPPRESS)
        # this pop hack: https://stackoverflow.com/questions/24180527/argparse-required-arguments-listed-under-optional-arguments
        parser._action_groups.pop()
        parser._positionals.title = 'Help Menu'
        parser.add_argument("(h)elp", help='Show this help menu')
        parser.add_argument("(n)ext [LEVEL]", help="Select next problem. Optionally, go next by level [(e)asy, (m)edium, (h)ard], default ignores levels. I.e. 'n' or 'n e' or 'next easy'" )
        parser.add_argument("(q)uestion NUMBER", help="Select problem by question number i.e. 'q 183' or 'question 183'")
        parser.add_argument("(s)olution", help='Open solution of current problem in webpage')
        parser.add_argument("(d)isplay [LEVEL] [# TO DISPLAY]", help="Displays list of problems. Optionally, can display by level [(e)asy, (m)edium, (h)ard]. Optionally, can also choose how many problems to display, default is {default1}. Ex: 'd' is to display next {default2} problems of all levels, 'd e 30' is to display the next 30 easy problems.".format(default1=default_num_to_display, default2=default_num_to_display))
        parser.add_argument("(e)xit", help='Exit program')
        self.parser = parser

    def print_help(self):
        print('\n')
        self.parser.print_help()
        time.sleep(2)

if __name__ == '__main__':
    help_menu = HelpMenu()
    help_menu.print_help()

