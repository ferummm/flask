import re
def validate(user):
    errors = dict()
    if len(user["name"]) < 4:
        errors["name"] = "Nickname must be grater than 4 symbols"
    
    if not validate_mail(user["email"]):
        errors["email"] = "Wrong email"

    return errors

def validate_mail(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$'
    return re.match(pattern, email)
