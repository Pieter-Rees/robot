from logging import Formatter, StreamHandler, DEBUG, ERROR, getLogger
from sys import stderr
from pyftdi import FtdiLogger
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

# Thread-safe logging setup
_logging_lock = threading.Lock()
_logging_initialized = False
_logger = None

# Thread pool for parallel logging operations
_logging_pool = ThreadPoolExecutor(max_workers=4)

def setup_logging(verbose=0, debug=False) -> int:
    """
    Set up logging configuration consistently across the application.
    Thread-safe implementation with parallel logging support.
    
    Args:
        verbose (int): Verbosity level (0-4)
        debug (bool): Whether to enable debug mode
        
    Returns:
        int: The configured log level
    """
    global _logging_initialized, _logger
    
    with _logging_lock:
        if _logging_initialized:
            return _logger.getEffectiveLevel()
            
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
        
        _logger = getLogger('robot')
        _logger.setLevel(loglevel)
        _logging_initialized = True
        
        return loglevel

def log_async(message: str, level: int = DEBUG) -> None:
    """
    Log a message asynchronously using the thread pool.
    
    Args:
        message (str): The message to log
        level (int): The logging level (default: DEBUG)
    """
    if not _logging_initialized:
        setup_logging()
    
    def _log():
        with _logging_lock:
            _logger.log(level, message)
    
    _logging_pool.submit(_log)

def cleanup_logging() -> None:
    """Clean up logging resources."""
    global _logging_initialized
    with _logging_lock:
        if _logging_initialized:
            _logging_pool.shutdown(wait=True)
            _logging_initialized = False

# Register cleanup handler
import atexit
atexit.register(cleanup_logging) 