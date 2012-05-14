#!/usr/local/bin/python2.7

import argparse
from datetime import datetime
import json
import os


_CONFIG = os.path.expanduser('~/.timetracker')
_DEFAULT_CONFIG = {
    'projects': {}
}


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
        if False:
            print self.config

        if self.save:
            with open(_CONFIG, 'w') as cf:
                json.dump(self.config, cf)


def start(args):

    def new_start():
        return {'start': str(datetime.now())}

    with Config() as config:
        if args.project in config['projects']:
            last = config['projects'][args.project][-1]
            if not 'stop' in last and not args.quiet:
                print '{} in progress as of {}'.format(args.project, last['start'])
            else:
                config['projects'][args.project].append(new_start())
        else:
            config['projects'][args.project] = [new_start()]
            if not args.quiet:
                print '{} (new) started'.format(args.project)


def stop(args):
    with Config() as config:
        if args.project in config['projects']:
            last = config['projects'][args.project][-1]
            if 'stop' in last and not args.quiet:
                print '{} stopped as of {}'.format(args.project, last['stop'])
            else:
                last['stop'] = str(datetime.now())
        else:
            if not args.quiet:
                print 'No project {}'.format(args.project)


def rm(args):
    with Config() as config:
        if args.project in config['projects']:
            if not args.force:
                confirm = raw_input('Remove project \'{}\'? (yes/no) '.format(args.project))
                if not confirm == 'yes':
                    print 'Aborted.'
                    return

            del config['projects'][args.project]
            if not args.quiet:
                print 'Deleted project {}'.format(args.project)
        else:
            if not args.quiet:
                print 'No project {}'.format(args.project)


def list(args):
    with Config(save=False) as config:
        for args.project in config['projects']:
            print args.project


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Time Tracker')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='no output')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='extra output')

    subparsers = parser.add_subparsers(title='commands')

    p_start = subparsers.add_parser('start', help='start tracking a project')
    p_start.add_argument('project', help='target (or new) project')
    p_start.set_defaults(func=start)

    p_stop = subparsers.add_parser('stop', help='stop tracking a project')
    p_stop.add_argument('project', help='target project')
    p_stop.set_defaults(func=stop)

    p_rm = subparsers.add_parser('rm', help='delete a project')
    p_rm.add_argument('project', help='target project')
    p_rm.add_argument('-f', '--force', action='store_true', help='do no prompt')
    p_rm.set_defaults(func=rm)

    p_list = subparsers.add_parser('list', help='list all projects')
    p_list.set_defaults(func=list)

    args = parser.parse_args()
    args.func(args)
