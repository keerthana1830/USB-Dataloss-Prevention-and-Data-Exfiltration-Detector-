"""
Utility functions for user identification
"""
import os
import getpass
import platform

def get_current_username():
    """
    Get the currently logged-in OS username
    Returns the username or 'Unknown' if unable to determine
    """
    try:
        # Try getpass first (most reliable)
        username = getpass.getuser()
        if username:
            return username
    except:
        pass
    
    try:
        # Try os.getlogin() as fallback
        username = os.getlogin()
        if username:
            return username
    except:
        pass
    
    try:
        # Try environment variables
        if platform.system() == "Windows":
            username = os.environ.get('USERNAME')
        else:
            username = os.environ.get('USER')
        
        if username:
            return username
    except:
        pass
    
    return "Unknown"
