import os, yaml

# Get or make config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
if os.path.isfile(config_path):
    config = yaml.safe_load(open(config_path))
else:
    config = {}
    f = open(config_path, "w")
    f.close()
# Set defaults if no config was found
if not config:
    # log_format contains formatting strings
    # by default, ANSI condes are used - could use markup tags instead, for example
    # TODO: Consider using a cross-platform solution for output formatting
    config["log_format"] = {
        "header": "\033[95m",	# Purple
        "info"	: "\033[94m",	# Blue
        "success":"\033[92m",	# Green
        "warn"	: "\033[93m",	# Yellow
        "fail"	: "\033[91m",	# Red
        "end"	: "\033[0m",	# Ends colored text
    }
    # force_print defines which, if any, log types to always print to console
    # this is irrelevant if verbose is true
    config["force_print"] = ["fail", ]
    config["verbose"] = True

    # Settings for logs messages printed to console
    config["show_timestamp"] = True
    config["show_caller"] = True

    # log_levels defines which, if any, log types to save in a log file
    # this only has an effect if keep_log is true
    config["log_levels"] = ["fail", "warn", ]
    config["keep_log"] = False

    # debug determines whether errors should raise and halt execution
    config["debug"] = False

    config["date_format"] = "%y-%m-%d"
    config["datetime_format"] = "%y-%m-%d %H:%M:%S"

    with open(config_path, "w") as f:
       yaml.dump(config, f)

__all__ = ["log", "file"]
