import subprocess
import threading
from queue import Queue
from typing import Self


class PersistentBash:
    def __init__(self):
        self.process = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        )
        self.stdout_queue = Queue()
        self.stderr_queue = Queue()
        self.stdout_thread = threading.Thread(target=self._read_stream, args=(self.process.stdout, self.stdout_queue))
        self.stderr_thread = threading.Thread(target=self._read_stream, args=(self.process.stderr, self.stderr_queue))
        self.stdout_thread.daemon = True
        self.stderr_thread.daemon = True
        self.stdout_thread.start()
        self.stderr_thread.start()

    def _read_stream(self, stream, queue):
        while True:
            line = stream.readline()
            if line:
                queue.put(line)
            else:
                break

    def _read_output(self, queue):
        output = []
        while not queue.empty():
            output.append(queue.get())
        return "".join(output)

    def run(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        self.stdout_thread.join(timeout=1)
        self.stderr_thread.join(timeout=1)
        stdout_output = self._read_output(self.stdout_queue)
        stderr_output = self._read_output(self.stderr_queue)

        if stderr_output:
            return stderr_output
        else:
            return stdout_output

    def close(self):
        self.process.stdin.write("exit\n")
        self.process.stdin.flush()
        self.process.wait()
        self.stdout_thread.join()
        self.stderr_thread.join()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
