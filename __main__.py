from sys import path
from os.path import abspath, dirname
from argparse import ArgumentParser

path.append(dirname(abspath('.')))


from mars.monitor import Monitor
from mars.frontend.cli_front import CLIFrontend
from mars.config_loaders.file_config_loader import FileConfigLoader

parser = ArgumentParser()
parser.add_argument('remotes', type=str, nargs='*', help='remotes to monitor')
parser.add_argument('-f',
                    '--file',
                    help='file with remotes to monitor each on the new line')


def main():
    config_loader = FileConfigLoader(r'conf.ini')
    app = Monitor(config_loader, CLIFrontend)
    from mars.checkers.ping_checker import PingChecker
    checkers_to_add = []
    for remote in parser.parse_args().remotes:
        checkers_to_add.append(app.config.default_checker(remote))
    if parser.parse_args().file:
        with open(parser.parse_args().file, 'r') as f:
            for remote in f:
                checkers_to_add.append(app.config.default_checker(remote.strip()))
    app.add_checkers_list(checkers_to_add)
    app.run()


if __name__ == '__main__':
    main()
