import itertools
import sys
import threading


class Spinner(object):
    spinner_cycle = itertools.cycle(["   🚢", "  🚢 ", " 🚢  ", "🚢   "])

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        self.stop_running = None
        self.spin_thread = None

    def start(self):
        if self.stream.isatty():
            self.stop_running = threading.Event()
            self.spin_thread = threading.Thread(target=self.init_spin)
            self.spin_thread.start()

    def stop(self):
        if self.spin_thread:
            self.stop_running.set()
            self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            self.stream.write(next(self.spinner_cycle))
            self.stream.flush()
            self.stop_running.wait(0.25)
            self.stream.write("\b\b\b\b")
            self.stream.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


def ship_spinner(beep=False, disable=False, force=False, stream=sys.stdout):
    """This function creates a context manager that is used to display a
    spinner on stdout as long as the context has not exited.
    The spinner is created only if stdout is not redirected, or if the spinner
    is forced using the `force` parameter.
    """
    return Spinner(stream)
