"""
    Simple logging facility the supports colors and types.
    Can write logs to a file and/or to console.
"""

from HandyLib import config
import os, sys, inspect, time

def log(message, log_type = "info", force = False, caller = False):
    """
        Logs events to console and/or log file.
        `message` should be any string you want to log
        `log_type` should be a key in the `log_format` dict in the config
            "info" if undefined
        `force` can be used to force printing to console
        `caller` defines the name of the calling function/module/package/whatever
            if undefined, will be module[.className] of calling function
        Stored logs will be named after the filename that calls this function.
    """

    # Try to figure out who we're logging for
    if not caller:
        stack = inspect.stack()[2]
        call_module = inspect.getmodulename(stack[1])
        # Try to get a className for caller
        if "self" in stack[0].f_locals:
            call_class = stack[0].f_locals["self"].__class__.__name__
            caller = "{}.{}".format(str(call_module), str(call_class))
        else:
            caller = str(call_module)

    # Handle invalid log types
    if not log_type in config["log_format"]:
        log("Invalid log_type specified by {0}: {1}".format(caller, log_type), "warn", True, __name__)
        log_type = "info"

    # Print if running in verbose mode or if "force" is true or if log type is configured to always print
    if config["verbose"] or force or log_type in config["force_print"]:
        if config["show_caller"] and config["show_timestamp"]:
            print( # Format: [caller] message - timestamp
                "{0}[{1}] {2} - {3}{4}".format(
                    config["log_format"][log_type],
                    caller,
                    message,
                    time.strftime(config["datetime_format"]),
                    config["log_format"]["end"]
                )
            )
        elif config["show_caller"]:
            print( # Format: [caller] message
                "{0}[{1}] {2}{3}".format(
                    config["log_format"][log_type],
                    caller,
                    message,
                    config["log_format"]["end"]
                )
            )
        elif config["show_timestamp"]:
            print( # Format: message - timestamp
                "{0}{1} - {2}{3}".format(
                    config["log_format"][log_type],
                    message,
                    time.strftime(config["datetime_format"]),
                    config["log_format"]["end"]
                )
            )
        else:
            print( # Format: message
                "{0}{1}{2}".format(
                    config["log_format"][log_type],
                    message,
                    config["log_format"]["end"]
                )
            )


    # Log to file if appropriate and possible
    if config["keep_log"]:
        log_path = os.path.join(os.getcwd(), "logs")
        # Can't use HandyLib.file.mkdir() because it would cause circular import... :(
        if not os.path.isdir(log_path):
            try:
                os.makedirs(log_path)
            except:
                config["keep_log"] = False
                log("Failed to create log directory! Log storage disabled.", "fail", True, __name__)
                if(config["debug"]): raise
                return
        with open(os.path.join(log_path, "{0}.log".format(call_module)), "a") as temp:
            temp.write( # Format: timestamp - message
                "{0}{1} - {2}{3}\n".format(
                    config["log_format"][log_type],
                    time.strftime(config["datetime_format"]),
                    message,
                    config["log_format"]["end"]
                )
            )

# Beware the dark arts
# https://stackoverflow.com/a/1060872
class log_caller(object):
    def __call__(self, *args, **kwargs):
        log(*args, **kwargs)
sys.modules[__name__] = log_caller()
