import logging
import sys 

def pilogger(klass):
    """This class decorator adds (if necessary) an instance
    of the logger (self._logger) to the attached class
    and removes from the getState the logger.

    """
    # Verify if a logger already exists
    found = False
    for k, v in klass.__dict__.items():
        if isinstance(v, logging.Logger):
            found = True
            break
    if not found:
        klass._logger = logging.getLogger(klass.__name__)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt = 'proinspector >> [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)'
        handler.setFormatter(logging.Formatter(fmt))
        klass._logger.addHandler(handler)
        klass._logger.propagate = False

    # Exclude logger from __getstate__
    def getState(self, **kwargs):
        r = dict()
        for k, v in self.__dict__.items():
            if not isinstance(v, logging.Logger):
                r[k] = v
        return r

    def setState(self, dict):
        self.__dict__ = dict
        self.__logger = logging.getLogger(klass.__name__)

    klass.__getstate__ = getState
    klass.__setState__ = setState


    return klass