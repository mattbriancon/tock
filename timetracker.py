#!/usr/local/bin/python2.7

import argparse
from collections import OrderedDict
from datetime import datetime, timedelta
import json
import logging
import os
from pprint import pprint
# import xdg


_CONFIG = os.path.expanduser('~/.timetracker')

logger = logging.getLogger('timetracker')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def now():
    return datetime.now().replace(microsecond=0)


def str_to_datetime(ts):
    format = '%Y-%m-%dT%H:%M:%S'
    return datetime.strptime(ts, format)


def delta_to_str(delta):
    hours = delta.days * 24 + delta.seconds / 3600
    minutes = delta.seconds % 3600 / 60
    seconds = delta.seconds % 60
    return '{}h{}m{}s'.format(hours, minutes, seconds)


class Project(object):

    def __init__(self, name, sessions=None):
        self.name = name
        self.sessions = sessions or []

        self._total = None

    def start(self):
        if not self.is_active:
            self.sessions.append({'start': now()})
        else:
            start = self.sessions[-1]['start'].isoformat()
            logger.warning('{} in progress as of {}'.format(self.name, start))

    def stop(self):
        if len(self.sessions) == 0:
            logging.info('{} has never been started'.format(self.name))

        last = self.sessions[-1]

        if self.is_active:
            last['stop'] = now()
            last['duration'] = last['stop'] - last['start']
        else:
            stop = last['stop'].isoformat()
            logging.info('{} has been inactive since {}'.format(self.name, stop))

    @property
    def total(self):
        if not self.is_active and self._total:
            return self._total

        total = timedelta()

        for session in self.sessions:
            if 'duration' in session:
                total += session['duration']
            else:
                total += now() - session['start']

        self._total = total if not self.is_active else None

        return total

    @property
    def is_active(self):
        try:
            return not 'stop' in self.sessions[-1]
        except:
            return False

    @property
    def current(self):
        if self.is_active:
            return now() - self.sessions[-1]['start']

        return timedelta()


class TimeTracker(object):

    def __init__(self):
        self.load_data()

    def load_data(self):
        try:
            with open(_CONFIG, 'r') as cf:
                self._raw_data = json.load(cf)
        except:
            self._raw_data = {'projects': {}}

        self.projects = OrderedDict()
        for name in self._raw_data['projects'].keys():

            sessions = []
            for session in self._raw_data['projects'][name]:

                session['start'] = str_to_datetime(session['start'])

                if 'stop' in session:
                    session['stop'] = str_to_datetime(session['stop'])
                    session['duration'] = timedelta(seconds=session['duration'])

                sessions.append(session)

            self.projects[name] = Project(name, sessions)

    def save_data(self):
        with open(_CONFIG, 'w') as cf:
            data = {'projects': {}}
            for project in self.projects.values():
                sessions = []
                for s in project.sessions:
                    s_dump = {'start': s['start'].isoformat()}

                    if 'stop' in s:
                        s_dump['stop'] = s['stop'].isoformat()
                        s_dump['duration'] = s['duration'].days * 24 * 60 * 60 + s['duration'].seconds

                    sessions.append(s_dump)

                data['projects'][project.name] = sessions

            json.dump(data, cf)

    # def _save(func):
    #     def wrapped():
    #         ret = func()
    #         save()
    #         return ret

    #     return wrapped

    # @save
    def start(self, name):
        try:
            self.projects[name].start()
        except KeyError:
            p = Project(name)
            p.start()
            self.projects[name] = p
            logging.info('created project \'{}\''.format(name))

        self.save_data()

    def stop(self, name):
        try:
            self.projects[name].stop()
            self.save_data()
        except KeyError:
            logger.warning('no such project \'{}\''.format(name))

    def delete(self, name):
        del self.projects[name]
        self.save_data()


def start(args):
    tt = TimeTracker()
    tt.start(args.project)


def stop(args):
    tt = TimeTracker()
    tt.stop(args.project)


def rm(args):
    if not args.force:
        logger.info('must supply force argument (-f/--force) to delete')
        return

    tt = TimeTracker()
    tt.delete()


def list(args):
    tt = TimeTracker()

    for project in tt.projects:
        logger.info(project)


def dump(args):
    tt = TimeTracker()
    pprint(tt._raw_data)


def status(args):
    tt = TimeTracker()

    prompt = []
    for project in tt.projects.values():
        if project.is_active:
            prompt.append('{project} T: {total} C: {current}'.format(**{
                'project': project.name,
                'total': delta_to_str(project.total),
                'current': delta_to_str(project.current),
            }))

    if len(prompt) > 0:
        print '[', ', '.join(prompt), ']'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Time Tracker')

    parser.add_argument('-q', '--quiet', action='store_true', help='no output')
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
    p_rm.add_argument('-f', '--force', action='store_true',
                      help='do no prompt')
    p_rm.set_defaults(func=rm)

    p_list = subparsers.add_parser('list', help='list all projects')
    p_list.set_defaults(func=list)

    p_dump = subparsers.add_parser('dump', help='dump data')
    p_dump.set_defaults(func=dump)

    subparsers.add_parser('status', help='status') \
            .set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)
