#!/usr/local/bin/python2.7

import argparse
from datetime import datetime
import json
import os


_CONFIG = os.path.expanduser('~/.time-tracker')
_DEFAULT_CONFIG = {
    'projects': {}
}

QUIET = False
VERBOSE = False
FORCE = False


class Config(object):
    def __init__(self, save=True):
        self.save = save

    def __enter__(self):
        try:
            with open(_CONFIG) as cf:
                self.config = json.load(cf)
        except:
            self.config = _DEFAULT_CONFIG

        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        if VERBOSE:
            print self.config

        if self.save:
            with open(_CONFIG, 'w') as cf:
                json.dump(self.config, cf)


def start(project):

    def new_start():
        return {'start': str(datetime.now())}

    with Config() as config:
        if project in config['projects']:
            last = config['projects'][project][-1]
            if not 'stop' in last:
                print '{} in progress as of {}'.format(project, last['start'])
            else:
                config['projects'][project].append(new_start())
        else:
            config['projects'][project] = [new_start()]
            print '{} (new) started'.format(project)


def stop(project):
    with Config() as config:
        if project in config['projects']:
            last = config['projects'][project][-1]
            if 'stop' in last:
                print '{} stopped as of {}'.format(project, last['stop'])
            else:
                last['stop'] = str(datetime.now())
        else:
            print 'No project {}'.format(project)


def rm(project):
    with Config() as config:
        if project in config['projects']:
            if not FORCE:
                confirm = raw_input('Remove project \'{}\'? (yes/no) '.format(project))
                if not confirm == 'yes':
                    print 'Aborted.'
                    return

            del config['projects'][project]
            print 'Deleted project {}'.format(project)
        else:
            print 'No project {}'.format(project)


def list(project):
    with Config(save=False) as config:
        for project in config['projects']:
            print project


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Time Tracker')

    parser.add_argument('command', type=str, help='start|stop|list|rm')
    parser.add_argument('project', type=str,
                        help='the project to interact with')
    parser.add_argument('-f', '--force', action='store_true',
                        help='do not prompt')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='no output')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='extra output')

    args = parser.parse_args()
    FORCE = args.force
    QUIET = args.quiet
    VERBOSE = args.verbose

    commands = {
            'start': start,
            'stop': stop,
            'rm': rm,
            'list': list,
    }
    commands[args.command](args.project)
