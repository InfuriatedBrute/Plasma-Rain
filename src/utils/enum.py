#https://stackoverflow.com/a/21889648
#example usage: states.py
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)