import os
import signal
import subprocess
import threading
import time

from api.anki_api import Anki


class AnkiProcess:
    ANKI_PROCESS: subprocess.Popen

    @classmethod
    def terminate(cls):
        os.kill(AnkiProcess.ANKI_PROCESS.pid, signal.SIGTERM)


def monitor_exe_process(exe_path):
    while True:
        process = subprocess.Popen(exe_path)
        AnkiProcess.ANKI_PROCESS = process
        process.wait()
        if process.returncode == signal.SIGTERM:
            print("Anki shutdown by signal.SIGTERM.")
            break
        elif process.returncode != 0:
            print(f"Anki crashed，error code: {process.returncode}，restarting...")
        else:
            print("anki shutdown normally.")
            break
        time.sleep(1)


def init_anki(anki_path):
    exe_path = anki_path
    monitor_thread = threading.Thread(target=monitor_exe_process, args=(exe_path,))
    monitor_thread.daemon = True
    monitor_thread.start()

    while True:
        try:
            Anki(port=18765)
            break
        except:
            print("Anki starting...")
            time.sleep(1)
    print("Anki successfully started!")


if __name__ == "__main__":
    init_anki(r"C:\Program Files\Anki\anki.exe")
