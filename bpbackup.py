# Example: daemonize pyinotify's notifier.
#
# Requires Python >= 2.5
import functools
import sys
import pyinotify
import ConfigParser

class Counter(object):
    """
    Simple counter.
    """
    def __init__(self):
        self.count = 0
    def plusone(self):
        self.count += 1

def on_loop(notifier, counter):
    """
    Dummy function called after each event loop, this method only
    ensures the child process eventually exits (after 5 iterations).
    """
    if counter.count > 4:
        # Loops 5 times then exits.
        sys.stdout.write("Exit\n")
        notifier.stop()
        sys.exit(0)
    else:
        sys.stdout.write("Loop %d\n" % counter.count)
        counter.plusone()

if __name__ == "__main__":

# Reading configration
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')
    pid_file = config.get('Runtime', 'pid_file')
    sync_log = config.get('Runtime', 'sync_log')
    error_log = config.get('Runtime', 'error_log')

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)
    wm.add_watch('/tmp', pyinotify.ALL_EVENTS)
    on_loop_func = functools.partial(on_loop, counter=Counter())

    try:
        notifier.loop(daemonize=True,
                    callback=on_loop_func,
                    stdout=sync_log,
                    pid_file=pid_file)
    except pyinotify.NotifierError, err:
        print >> sys.stderr, err
