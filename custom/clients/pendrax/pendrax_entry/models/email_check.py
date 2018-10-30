
def check_email(email):
    if email:
        if "@" in email:
            x, y = email.split("@")
            if "." in y:
                a, b = y.split(".")
                if len(a) > 1 and len(b) > 1:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False