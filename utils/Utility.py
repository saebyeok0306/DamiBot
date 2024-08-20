
def is_test_version():
    import sys
    argv_len = len(sys.argv)

    if argv_len == 1:
        return False

    if "--test" in sys.argv:
        return True

    return False
