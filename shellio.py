#!/usr/bin/env python

"""
IO interface for a shell PIPE

(c)copyright 2015,2017 Sungju Kwon
"""

import os, sys
from subprocess import Popen, PIPE
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

class ShellIO:
    show_prompt = False
    command_pipe = None
    jobdone = False
    out_port = sys.stdout
    in_port = sys.stdin

    def __init__(self):
        self.show_prompt = False
        self.command_pipe = None
        self.jobdone = False

    def set_output(self, output):
        self.out_port = output

    def set_input(self, input):
        self.in_port = input

    def enqueue_output(self, queue, out):
        for line in iter(out.readline, b''):
            if queue.closed:
                break
            queue.put(line)
        out.close()
        self.jobdone = True
        self.out_port.write('enqueue_output()\n')

    def catch_output(self, pipe, queue, prompt,
                     output_end_mark_str):
        while True:
            if queue.closed == True or self.jobdone == True:
                break
            try:
                line = queue.get_nowait()
            except Empty:
                if (self.show_prompt == False):
                    self.show_prompt = True
                    self.out_port.write(prompt)
                    self.out_port.flush()
                pass
            except IOError:
                break
            else:
                if (line.startswith(output_end_mark_str)):
                    self.show_prompt = False
                else:
                    self.out_port.write(line)

        self.in_port.close()
        self.out_port.write('catch_output()\n')
        return

    def catch_input(self, pipe, queue,
                    input_end_mark_str, start_first = False):
        if (start_first == True and input_end_mark_str != None):
            pipe.stdin.write(input_end_mark_str)

        while True:
            while (queue.empty() == False and self.jobdone == False):
                pass
            if (self.jobdone == True):
                break
            try:
                line = self.in_port.readline()
                pipe.stdin.write(line + "\n")
                if (input_end_mark_str != None):
                    pipe.stdin.write(input_end_mark_str)
            except (KeyboardInterrupt, SystemExit):
                break
            except IOError:
                break

        self.out_port.write('catch_input()\n')
        queue.closed = True
        pipe.stdin.close()
        return

    def start_command(self, command, prompt,
                      input_end_mark_str, output_end_mark_str,
                      input_start_first = False):
        if (input_start_first == True):
            self.show_prompt = True

        self.command_pipe = Popen(command, stdin = PIPE,
                                  stdout = PIPE, stderr = PIPE,
                                  bufsize = 1)
        queue = Queue()
        queue.closed = False
        thread_stdout_queue = Thread(target = self.enqueue_output,
                              args = (queue, self.command_pipe.stdout))
        thread_stdout_queue.daemon = True
        thread_stdout_queue.start()
        thread_stderr_queue = Thread(target = self.enqueue_output,
                              args = (queue, self.command_pipe.stderr))
        thread_stderr_queue.daemon = True
        thread_stderr_queue.start()

        thread_input = Thread(target = self.catch_input,
                              args = (self.command_pipe, queue,
                                      input_end_mark_str,
                                      input_start_first))
        thread_input.start()

        thread_output = Thread(target = self.catch_output,
                               args = (self.command_pipe, queue,
                                       prompt, output_end_mark_str))
        thread_output.start()


def unit_test():
    myshell = ShellIO()
    myshell.set_output(sys.stdout)
    myshell.set_input(sys.stdin)

    """
    myshell.start_command(["retrace-server-interact", "884323438", "crash"],
                          "crash> ",
                          "!echo 'crash> '\n",
                          "crash> ", True)
    """

    myshell.start_command(["bash"], "$ ",
                          "echo '======================='\n",
                          "=======================")


if __name__ == "__main__":
    unit_test()
