import re as _re

MAX_TYPOS = 2

def simplify(string): # HEAVILY INEFFICIENT LMFAOOOOO
    return _re.sub("[\(\[].*!?[\)\]]", "", string).strip().replace("'","").replace('♪', '').lower()
