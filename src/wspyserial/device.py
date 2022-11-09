from serial import Serial
from threading import Event
from .protocol import Package_Manager, package as pkg
from os import _exit, environ
from time import sleep
import sys
import uuid
from serial.serialutil import SerialException
def docker_exit():
    if environ.get('DOCKER'):
        _exit(1)

class Device():
    def __init__(self, device_id=0, baudrate=115200, _id=None, fail_callback=docker_exit, max_attemps=5, **kwargs):
        self.fail_callback = fail_callback
        self._id = uuid.uuid4() if _id is None else _id
        self.answers = {}
        self.stopped = Event()
        self.__cant_start = None
        self.__device_id = device_id
        self.__port_prefix = '/dev/ttyACM' if sys.platform.startswith('linux') else 'COM'
        self.__baudrate = baudrate
        self.open(max_attemps=max_attemps, **kwargs)
        self.clean_input()
        self.organizer = Package_Manager(self.writer, self.reader, whiout_start=self.__cant_start)
    
    def open(self, max_attemps=3, **kwargs):
        for _ in range(max_attemps):
            try:
                self.serial = Serial(port=self.__port_prefix+str(self.__device_id), baudrate=self.__baudrate, timeout=0)
                break
            except Exception as e:
                print(e)
                sleep(1)
        else:
            if kwargs.get('force_create') in (False, None):
                raise Exception("Serial port not found")
            else:
                self.__cant_start = True

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
    
    def clean_input(self):
        self.serial.flush()
        self.serial.flushInput()
        while self.serial.inWaiting() != 0:
            self.serial.readline()
        self.serial.flushInput()
        self.serial.flush()

    def stop(self):
        try:
            self.organizer.stop()
            self.stopped.set()
            # self.serial.close() #! Sometimes readLine() raise OSERROR (bad descriptor).
        finally:
            if self.fail_callback is not None:
                self.fail_callback()

    def __read(self):
        if not self.stopped.is_set() and self.serial.isOpen():
            return self.serial.readline()
        return b""

    def reader(self):
        lines = []
        _b = self.__read()
        while _b != b"":
            try:
                lines.append(_b.decode("ascii").rstrip())
            except UnicodeDecodeError:
                pass
            if self.serial.inWaiting() == 0:
                break
            _b = self.__read()
        if lines:
            return lines

    def writer(self, payload:str):
        try:
            self.serial.write((f"{payload}\n").encode("ascii"))
        except SerialException:
            self.stop()
    
    #! Move to organizer?? or create another class as parent from this.
    def read(self, _id, event, timeout=20):
        if isinstance(event, Event) and event.wait(timeout):
            return self.organizer.processed_answers.pop(_id)

    def send(self, package, timeout=None):
        if not isinstance(package, pkg):
            raise TypeError(f"package must be instance of {pkg}")
        self.organizer.packages.put(package, timeout=timeout)
        return package._id, package.event