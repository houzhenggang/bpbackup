#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import functools
import sys
import pyinotify
import ConfigParser
import logging
import pybcs

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, bucket):
        self.bucket = bucket

    def process_IN_CREATE(self, event):
        logging.debug(event)
        o = self.bucket.object(event.pathname)
        o.put_file(event.pathname)
        logging.debug('upload successfully')

    def process_IN_DELETE(self, event):
        logging.debug(event)
        o = self.bucket.object(event.pathname)
        o.delete()
        logging.debug('delete successfully')

    def process_IN_MODIFY(self, event):
        logging.debug(event)

def main(argv):

# Reading configration
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')

    pid_file = config.get('Runtime', 'pid_file')
    log_file = config.get('Runtime', 'log_file')

    bcs_url = config.get('Baidu', 'bcs_url')
    bucket_name = config.get('Baidu', 'bucket_name')
    api_key = config.get('Baidu', 'api_key')
    secret_key = config.get('Baidu', 'secret_key')

# Create logging
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(filename = log_file,
            level = logging.DEBUG,
            format = LOG_FORMAT)
    logging.info("Baidu Pan Backup daemon start.")

# Connect to BCS
    bcs = pybcs.BCS(bcs_url, api_key, secret_key)
    b = bcs.bucket(bucket_name)

# Create watching manager
    wm = pyinotify.WatchManager()
# Loading watching dirs
    watching_dirs = dict(config.items('Watching_dirs'))
    logging.info("Loading watching dirs.")
# Adding watching dirs
    for d in watching_dirs.values():
        wm.add_watch(d, pyinotify.ALL_EVENTS)
        logging.info("Adding %s" % (d))

    handler = EventHandler(b)
    notifier = pyinotify.Notifier(wm, handler)
    #sync_func = functools.partial(on_sync, counter=Counter())

    try:
        notifier.loop(daemonize=False,
                    pid_file=pid_file)
    except pyinotify.NotifierError, err:
        logging.error(err)

if __name__ == "__main__":
    main(sys.argv)
