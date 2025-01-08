from flask import redirect, session
from functools import wraps


# Check if user is logged in
def login_required(f):
    """
    Checks if the "user_id" key exists:
    if it does not redirect to the login page (/login),
    if exists it calls the original function with the arguments passed.
    """
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function