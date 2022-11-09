import queue
from threading import Thread, Event
import uuid
import random

class package:
    def __init__(self, data, answer_lines=1, _id=None, read=True):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.event = Event()
        self.data = data
        self.answer_lines = answer_lines
        self.read = read
    
    def __repr__(self):
        return f"package({self.data}, {self.answer_lines})"
    
    def __str__(self):
        return self.__repr__()

    def json(self):
        return {"_id": self._id, "data": self.data, "answer_lines": self.answer_lines, "read": self.read}

class Package_Manager:
    def __init__(self, writer, reader, **kwargs) -> None:
        self.__limit = -1
        self.packages = queue.Queue(self.__limit)
        self.answers = queue.Queue(self.__limit)
        self.answers_order = queue.Queue(self.__limit)
        self.stopped = Event()
        self.processed_answers = {}

        self.writer = writer
        self.reader = reader

        self.producer_thread = Thread(target=self.producer, daemon=True)
        self.consumer_thread = Thread(target=self.consumer, daemon=True)
        self.processor_thread = Thread(target=self.processor, daemon=True)

        if kwargs.get('whiout_start') is None:
            self.start()
       
    def start(self):
        self.producer_thread.start()
        self.consumer_thread.start()
        self.processor_thread.start()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def stop(self):
        self.stopped.set()
    
    def is_stopped(self):
        return self.stopped.is_set()

    def producer(self):
        while not self.is_stopped():
            package = self.packages.get()
            self.packages.task_done()
            self.answers_order.put(package)
            self.writer(package.data)
        
    
    def consumer(self):
        while not self.is_stopped():
            answer = self.reader()
            if isinstance(answer, list) and any(answer):
                for msg in answer:
                    self.answers.put(msg)
            elif answer is not None:
                self.answers.put(answer)

    
    def processor(self):
        while not self.is_stopped():
            package = self.answers_order.get()
            self.answers_order.task_done()
            answers = []
            for _ in range(package.answer_lines):
                data = self.answers.get()
                self.answers.task_done()
                if package.read:
                    answers.append(data)
            if answers != []:
                self.processed_answers[package._id] = answers
                package.event.set()
        

def example_packages(qtd):
    packages = []
    for _ in range(qtd):
        _id = uuid.uuid4().hex
        data = F"M118 {_id}"
        read = bool(random.getrandbits(1))
        packages.append(package(data, 2, _id, read))
    return packages