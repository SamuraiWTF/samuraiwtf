#! /usr/bin/python3
import wtfcore
import argparse
import wtferrors
import os


def list_modules(args):
    results = wtfcore.list_modules()
    for mod in results:
        print("{} - {}".format(mod.get_name(), mod.get_description()))
    print(results)  # TODO: Pretty-print this


def install_module(args):
    wtfcore.install_module(args.name)


def remove_module(args):
    wtfcore.remove_module(args.name)


def start_module(args):
    wtfcore.start_module(args.name)


def stop_module(args):
    wtfcore.stop_module(args.name)


if __name__ == "__main__":
    if not os.geteuid() == 0:
        print("\nWARNING: This script must be run as root. Please type 'sudo' before the command.\n")
        exit(1)

    parser = argparse.ArgumentParser(description='Utility for managing SamuraiWTF modules.')
    subparsers = parser.add_subparsers()

    list = subparsers.add_parser('list')
    # list.add_argument('bar')
    list.set_defaults(func=list_modules)

    install = subparsers.add_parser('install')
    install.add_argument('name')
    install.set_defaults(func=install_module)

    remove = subparsers.add_parser('remove')
    remove.add_argument('name')
    remove.set_defaults(func=remove_module)

    start = subparsers.add_parser('start')
    start.add_argument('name')
    start.set_defaults(func=start_module)

    stop = subparsers.add_parser('stop')
    stop.add_argument('name')
    stop.set_defaults(func=stop_module)

    args = parser.parse_args()

    try:
        if 'func' in args:
            args.func(args)
        else:
            parser.print_usage()
    except wtferrors.WTFError as err:
        print("ERROR {}".format(err.message))
        parser.print_usage()
