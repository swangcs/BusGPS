import os
import csv


def main():
    # adapt the home folder of your datafile here
    home_dir = "/Users/shenwang/Desktop/busgps/v2/tmp/46/"
    with os.scandir(home_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):
                with open(home_dir + entry_name, "r") as csv_in:
                    cr = csv.reader(csv_in)
                    next(cr, None)  # skip header
                    prev = -1.0
                    for row in cr:
                        cur = float(row[0])
                        if cur <= prev:
                            print(entry_name)
                            print(cur)
                        prev = cur


if __name__ == '__main__':
    # it would NOT print anything, if all points are in monotonically increasing order
    main()
