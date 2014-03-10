#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import functools
import sys
import pyinotify
import ConfigParser
import logging

class Counter(object):
    """
    Simple counter.
    """
    def __init__(self):
        self.count = 0
    def plusone(self):
        self.count += 1

def on_sync(notifier, counter):
    if counter.count > 4:
        # Loops 5 times then exits.
        logging.info("Exit")
        notifier.stop()
        sys.exit(0)
    else:
        logging.info("Loop %d" % (counter.count))
        counter.plusone()

def main(argv):

# Reading configration
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')

    pid_file = config.get('Runtime', 'pid_file')
    log_file = config.get('Runtime', 'log_file')

# Create logging
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(filename = log_file,
            level = logging.DEBUG,
            format = LOG_FORMAT)
    logging.info("Baidu Pan Backup daemon start.")

# Create watching manager
    wm = pyinotify.WatchManager()
# Loading watching dirs
    watching_dirs = dict(config.items('Watching_dirs'))
    logging.info("Loading watching dirs.")
# Adding watching dirs
    for d in watching_dirs.values():
        wm.add_watch(d, pyinotify.ALL_EVENTS)
        logging.info("Adding %s" % (d))

    notifier = pyinotify.Notifier(wm)
    sync_func = functools.partial(on_sync, counter=Counter())

    try:
        notifier.loop(daemonize=True,
                    callback=sync_func,
                    pid_file=pid_file)
    except pyinotify.NotifierError, err:
        logging.error(err)

if __name__ == "__main__":
    main(sys.argv)
