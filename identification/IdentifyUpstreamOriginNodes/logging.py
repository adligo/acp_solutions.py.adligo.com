from typing import Callable

class Logger:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

    def __init__(self, name: str, logLevel: int):
        self.name = name
        self.logLevel = logLevel

    def getName(self):
        return self.name


    def log(self, level: int, messageSupplier: Callable[..., str]):
        """
        :param messageSupplier: delays construction of the string until
            usage is needed
        :return:
        """
        if level >= self.logLevel:
            print(messageSupplier())

    def getLevel(self):
        return self.logLevel


class LogConfig:
    def __init__(self, defaultLevel: int, loggers: dict[str,Logger] = None, levels: dict[str, int] = None):
        if loggers is None:
            self.loggers = {}
        else:
            self.loggers = loggers.copy()
        self.defaultLevel = defaultLevel
        if levels is None:
            self.levels = {}
        else:
            self.levels = levels.copy()

    def getLevel(self, logName: str) -> int:
        if logName in self.levels:
            return self.levels[logName]
        return self.defaultLevel

    def getLog(self, logName: str) -> Logger:
        if logName in self.loggers:
            return self.loggers[logName]
        log = Logger(logName, self.defaultLevel)
        self.loggers[logName] = log
        return log