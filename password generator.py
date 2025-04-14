import random

ranges = {
    "lowercase": lambda: map(lambda x:chr(x),range(ord('a'), ord('z') + 1)),
    "uppercase" : lambda: map(lambda x:chr(x),range(ord('A'), ord('Z') + 1)),
    "numbers" : lambda: map(lambda x:chr(x),range(ord('0'), ord('9') + 1)),
    "spesiel_chars": lambda:  ["!", "#", "$", "@", "&", "%",]
}

def get_range(allwed_chars):
    arr = []
    for i in allwed_chars:
        arr.extend(ranges[i]())
    return arr

def generate(len, allwed_chars):
    ALLOWED_CHARS = get_range(allwed_chars)
    print(ALLOWED_CHARS)
    output = ""
    for i in range(0, len):
        output += random.choice(ALLOWED_CHARS)
    print(output)

generate(12,("lowercase", "uppercase", "numbers", "spesiel_chars"))