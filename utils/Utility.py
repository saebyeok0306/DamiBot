
def is_test_version():
    import sys
    argv_len = len(sys.argv)

    if argv_len == 1:
        return False

    if "--test" in sys.argv:
        return True

    return False


def diff_int(value1:int, value2:int):
    diff = value1 - value2
    if diff > 0:
        return f"{diff}↑"
    elif diff < 0:
        return f"{abs(diff)}↓"
    else:
        return f"0＃"


def diff_float(value1:float, value2:float):
    diff = value1 - value2
    if diff > 0:
        return f"{diff:.2f}↑"
    elif diff < 0:
        return f"{abs(diff):.2f}↓"
    else:
        return f"0＃"