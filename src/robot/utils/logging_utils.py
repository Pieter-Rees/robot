from logging import Formatter, StreamHandler, DEBUG, ERROR
from sys import stderr
from pyftdi import FtdiLogger

def setup_logging(verbose=0, debug=False):
    """
    Set up logging configuration consistently across the application.
    
    Args:
        verbose (int): Verbosity level (0-4)
        debug (bool): Whether to enable debug mode
        
    Returns:
        int: The configured log level
    """
    loglevel = max(DEBUG, ERROR - (10 * verbose))
    loglevel = min(ERROR, loglevel)
    
    if debug:
        formatter = Formatter('%(asctime)s.%(msecs)03d %(name)-20s %(message)s', 
                            '%H:%M:%S')
    else:
        formatter = Formatter('%(message)s')
        
    FtdiLogger.set_formatter(formatter)
    FtdiLogger.set_level(loglevel)
    FtdiLogger.log.addHandler(StreamHandler(stderr))
    
    return loglevel 