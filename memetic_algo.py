import sys
sys.path.insert(0, 'utils/')

import load_data


def main():
    runtime = sys.argsv[-1]
    data = load_data.load(sys.argsv[1:-1])
    pass


if __name__ == "__main__":
    main()
