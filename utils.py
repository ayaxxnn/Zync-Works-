import random
import string

def generate_random_key(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
