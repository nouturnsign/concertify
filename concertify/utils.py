import re as _re
def simplify(string): # HEAVILY INEFFICIENT LMFAOOOOO
    return _re.sub("[\(\[].*!?[\)\]]", "", string).strip().replace("'","").lower()
