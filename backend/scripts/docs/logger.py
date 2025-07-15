# scripts/docs/logger.py
import sys

def log(message: str, level: str = "INFO", verbose: bool = False):
    """A consistent logger for all build scripts."""
    if level == "DEBUG" and not verbose:
        return

    icons = {"INFO": "[i]", "SUCCESS": "[+]", "WARNING": "[!]", "ERROR": "[x]", "DEBUG": "[?]"}
    prefix = icons.get(level, '   ')
    
    stream = sys.stderr if level in ["ERROR", "WARNING"] else sys.stdout
    
    lines = str(message).split('\n')
    for line in lines:
        if line.strip():
            print(f"{prefix}  {line}", file=stream)
        else:
            print(file=stream)