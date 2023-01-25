import itertools
import threading

import click


class Spinner(object):
    # ["   🚢", "  🚢 ", " 🚢  ", "🚢   "]
    # Unfortunately, backspacing doesn't seem to work correctly for emoji in iTerm, so leaving the "spinner"
    # as adding ships for now
    spinner_cycle = itertools.cycle(["🚢"])

    def __init__(self):
        self.stop_running = None
        self.spin_thread = None

    def start(self):
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.init_spin)
        self.spin_thread.start()

    def stop(self):
        if self.spin_thread:
            self.stop_running.set()
            self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            click.echo(next(self.spinner_cycle), nl=False)
            self.stop_running.wait(1)
            # click.echo("\b", nl=False)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


def ship_spinner():
    """This function creates a context manager that is used to display a
    spinner on stdout as long as the context has not exited.
    The spinner is created only if stdout is not redirected, or if the spinner
    is forced using the `force` parameter.
    """
    return Spinner()
