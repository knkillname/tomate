import datetime
import itertools
import json
import tkinter as tk
from tkinter import font, ttk


class TimerView(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.load_settings()

        self.current_timer = None
        self.started = None
        self.duration = None
        self.tick_interval = self.settings['tick_interval']
        self.is_ticking = False

        self.progress_var = tk.DoubleVar(self, 52.0)
        self.clock_var = tk.StringVar(self, '15:34')
        self.counter_var = tk.StringVar(self, '4')
        self.status_var = tk.StringVar(self, 'Long break')
        self.control_var = tk.StringVar(self, 'Stop')

        self.set_next_timer()
        self.stop()

        self.create_widgets()

    def load_settings(self, filename='settings.json'):
        with open(filename, 'rt', encoding='utf8') as file:
            self.settings = json.load(file)
        self.timers = itertools.cycle(self.settings['timers'])

    def tick(self):
        if not self.is_ticking:
            return
        elapsed = datetime.datetime.now() - self.started
        minutes, seconds = divmod(elapsed.seconds, 60)
        if elapsed <= self.duration:
            self.clock_var.set(f'{minutes:02d}:{seconds:02d}')
            self.progress_var.set(100*(elapsed/self.duration))
        else:
            self.set_next_timer()
            self.start()
        self.after(self.tick_interval, self.tick)

    def start(self):
        self.started = datetime.datetime.now()
        self.is_ticking = True
        if self.current_timer['can_skip']:
            self.control_var.set('Skip')
        else:
            self.control_var.set('Stop')
        self.tick()

    def stop(self):
        self.started = None
        self.clock_var.set('00:00')
        self.progress_var.set(0.0)
        self.is_ticking = False
        self.control_var.set('Start')

    def button_press(self):
        if self.is_ticking and self.current_timer['can_skip']:
            self.set_next_timer()
            self.start()
        elif self.is_ticking and not self.current_timer['can_skip']:
            self.stop()
        else:
            self.start()

    def set_next_timer(self):
        self.current_timer = next(self.timers)
        self.duration = datetime.timedelta(
            minutes=self.current_timer['minutes'])
        self.status_var.set(self.current_timer['status'])
        self.counter_var.set(self.current_timer['counter'])

    def create_widgets(self):
        font_family = self.settings['font_family']
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._progress_frame = ttk.Frame(self)
        self._progress_frame.grid(
            row=0, column=0, rowspan=2, pady=21, sticky=tk.NS)
        self._progress_frame.rowconfigure(0, weight=1)
        self._progress_bar = ttk.Progressbar(
            master=self._progress_frame,
            orient=tk.VERTICAL,
            maximum=100,
            variable=self.progress_var)
        self._progress_bar.grid(row=0, column=0, sticky=tk.NS)
        self._counter_label = ttk.Label(
            self._progress_frame,
            font=font.Font(family=font_family, size=21),
            textvariable=self.counter_var)
        self._counter_label.grid(row=1, column=0, sticky=None)

        self._clock_frame = ttk.Frame(self)
        self._clock_frame.grid(
            row=0, column=1, padx=13, pady=13, sticky=None)
        self._clock_label = ttk.Label(
            master=self._clock_frame,
            font=font.Font(family=font_family, size=34, weight=font.BOLD),
            textvariable=self.clock_var)
        self._clock_label.grid(row=0, column=0, sticky=None)
        self._status_label = ttk.Label(
            master=self._clock_frame,
            font=font.Font(family=font_family, size=13),
            textvar=self.status_var)
        self._status_label.grid(row=1, column=0, sticky=None)

        self._controls_frame = ttk.Frame(self)
        self._controls_frame.grid(row=1, column=1, sticky=None)
        self._start_button = ttk.Button(
            self._controls_frame, textvar=self.control_var,
            command=self.button_press)
        self._start_button.grid(row=0, column=0, sticky=None)


if __name__ == '__main__':
    ROOT = tk.Tk()
    ROOT.minsize(640, 480)
    ROOT.columnconfigure(0, weight=1)
    ROOT.rowconfigure(0, weight=1)
    ROOT.style = ttk.Style(ROOT)
    ROOT.style.theme_use('clam')
    ROOT._timer_frame = TimerView(ROOT)
    ROOT.mainloop()
