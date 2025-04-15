import random
import argparse

ranges = {
    "lowercase": lambda: map(lambda x:chr(x),range(ord('a'), ord('z') + 1)),
    "uppercase" : lambda: map(lambda x:chr(x),range(ord('A'), ord('Z') + 1)),
    "numbers" : lambda: map(lambda x:chr(x),range(ord('0'), ord('9') + 1)),
    "special": lambda:  ["!", "#", "$", "@", "&", "%"]
}

def get_range(allowed_chars):
    arr = []
    for i in allowed_chars:
        arr.extend(ranges[i]())
    return arr

def generate(length, allowed_chars):
    ALLOWED_CHARS = get_range(allowed_chars)
    output = ""
    for i in range(0, length):
        output += random.choice(ALLOWED_CHARS)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a random password with specified options')
    parser.add_argument('--length', '-l', type=int, default=12, help='Length of the password (default: 12)')
    parser.add_argument('--lowercase', action='store_true', help='Include lowercase letters')
    parser.add_argument('--uppercase', action='store_true', help='Include uppercase letters')
    parser.add_argument('--numbers', action='store_true', help='Include numbers')
    parser.add_argument('--special', action='store_true', help='Include special characters')
    parser.add_argument('--all', '-a', action='store_true', help='Include all character types')

    args = parser.parse_args()

    # If no character types are specified or --all is used, enable all types
    if not any([args.lowercase, args.uppercase, args.numbers, args.special]) or args.all:
        args.lowercase = args.uppercase = args.numbers = args.special = True

    char_types = []
    if args.lowercase:
        char_types.append("lowercase")
    if args.uppercase:
        char_types.append("uppercase")
    if args.numbers:
        char_types.append("numbers")
    if args.special:
        char_types.append("special")

    password = generate(args.length, char_types)
    print(password)