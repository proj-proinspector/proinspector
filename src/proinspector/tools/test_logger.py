import logging

logger=logging.getLogger(__name__)
handler=logging.StreamHandler()
log_format = logging.Formatter('Test >> [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)')
handler.setFormatter(log_format)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
log_test = logger.debug
