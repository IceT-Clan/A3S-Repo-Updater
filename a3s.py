#!/usr/bin/env python3
import argparse


def main():
    # Command line argument setup
    parser = argparse.ArgumentParser(description="Arma 3 Repository Updater")
    parser.add_argument("-a", "--add", help="Add mod to repository")
    parser.add_argument("-r", "--remove", help="Remove mod from repository")
    parser.add_argument("-u", "--update", help="Update repository")

    args = parser.parse_args()

    return

if __name__ == "__main__":
    main()
