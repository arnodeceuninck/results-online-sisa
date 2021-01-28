import pickle

def load_pickle(name, default):
    try:
        var = pickle.load(open(name, "rb"))
    except (OSError, IOError):
        var = default
    return var


def store_pickle(name, var):
    pickle.dump(var, open(name, "wb"))