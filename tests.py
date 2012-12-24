

from datetime import timedelta, datetime
import logging
from mock import MagicMock, patch
import os
import tempfile
import unittest

import timetracker
from timetracker import Project

timetracker.logger.setLevel(logging.INFO)


class TimeTrackerTest(unittest.TestCase):

    def setUp(self):
        self.default_config = timetracker._CONFIG
        fd, path = tempfile.mkstemp()
        os.close(fd)
        timetracker._CONFIG = path

        self.tt = timetracker.TimeTracker()

    def test_create_default_data(self):
        self.assertTrue('projects' in self.tt._raw_data)

    def test_save_changes(self):
        self.tt.start('new-project')

        tt2 = timetracker.TimeTracker()
        self.assertEqual(len(self.tt.projects), len(tt2.projects))

    def test_start(self):
        self.tt.start('new-project')
        self.assertEqual(1, len(self.tt.projects))
        self.tt.start('test')
        self.assertEqual(2, len(self.tt.projects))

    def test_stop(self):
        mock_logger = MagicMock()
        with patch('timetracker.logger', mock_logger):
            self.tt.stop('new-project')
            mock_logger.warning.assert_call_with()
            args = mock_logger.warning.call_args[0][0]
            self.assertTrue('no such project' in args)

    def tearDown(self):
        os.unlink(timetracker._CONFIG)
        timetracker._CONFIG = self.default_config


class ProjectTest(unittest.TestCase):

    def setUp(self):
        self.p = Project('new-project')

    def test_start(self):
        xmas_eve = datetime(2012, 12, 24)
        with patch('timetracker.now', new=MagicMock(return_value=xmas_eve)):
            self.p.start()
            self.assertEqual(1, len(self.p.sessions))
            last = self.p.sessions[-1]
            self.assertEqual(xmas_eve, last['start'])

    def test_stop(self):
        self.p.start()

        last = self.p.sessions[-1]
        last['start'] = last['start'].replace(year=2000)

        self.p.stop()

        self.assertLess(last['start'], last['stop'])
        self.assertEqual(last['duration'], last['stop'] - last['start'])

    def test_is_active(self):
        self.assertFalse(self.p.is_active)
        self.p.start()
        self.assertTrue(self.p.is_active)
        self.p.stop()
        self.assertFalse(self.p.is_active)

    def test_current(self):
        self.assertEqual(timedelta(), self.p.current)

        with patch('timetracker.now',
                new=MagicMock(return_value=datetime(2012, 12, 22))):
            self.p.start()

        with patch('timetracker.now',
                new=MagicMock(return_value=datetime(2012, 12, 24))):
            self.assertEqual(timedelta(days=2), self.p.current)

    def test_total(self):
        self.p.sessions = [
            {
                'start': datetime(2012, 12, 20, 12),
                'stop': datetime(2012, 12, 20, 14),
            },
            {
                'start': datetime(2012, 12, 21, 12),
                'stop': datetime(2012, 12, 21, 14),
            },
            {
                'start': datetime(2012, 12, 22, 12),
                'stop': datetime(2012, 12, 22, 14),
            },
        ]

        for s in self.p.sessions:
            s['duration'] = s['stop'] - s['start']

        self.assertEqual(timedelta(seconds=6 * 60 * 60), self.p.total)

        with patch('timetracker.now',
                new=MagicMock(return_value=datetime(2012, 12, 23, 14))):
            self.p.sessions.append({
                    'start': datetime(2012, 12, 23, 12),
            })

            self.assertEqual(timedelta(seconds=8 * 60 * 60), self.p.total)


if __name__ == '__main__':
    unittest.main()
