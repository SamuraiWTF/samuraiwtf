#! /usr/bin/python3
import katanacore
import argparse
import katanaerrors
import os


def list_modules(args):
    results = katanacore.list_modules()
    for mod in results:
        print("{} - {}".format(mod.get_name(), mod.get_description()))  # TODO: Pretty-print this


def install_module(args):
    katanacore.install_module(args.name)


def remove_module(args):
    katanacore.remove_module(args.name)


def start_module(args):
    katanacore.start_module(args.name)


def stop_module(args):
    katanacore.stop_module(args.name)


def status_module(args):
    print("Status: {}".format(katanacore.status_module(args.name)))

def lock_modules(args):
    katanacore.lock_modules()
    print("Modules are locked. Check katana.lock file to verify list.")


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

    status = subparsers.add_parser('status')
    status.add_argument('name')
    status.set_defaults(func=status_module)

    lock = subparsers.add_parser('lock')
    lock.set_defaults(func=lock_modules)

    args = parser.parse_args()

    try:
        if 'func' in args:
            args.func(args)
        else:
            parser.print_usage()
    except katanaerrors.WTFError as err:
        print("ERROR {}".format(err.message))
        parser.print_usage()
