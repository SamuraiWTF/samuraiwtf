#! /usr/bin/python3
import wtfcore
import argparse


def list_modules(args):
	results = wtfcore.list_modules()
	print(results)  #TODO: Pretty-print this

def install_module(args):
  print("Installing...")
  results = wtfcore.install_module(args.name)
  print(results)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utility for managing SamuraiWTF modules.')
  subparsers = parser.add_subparsers()

  list = subparsers.add_parser('list')
  # list.add_argument('bar')
  list.set_defaults(func=list_modules)

  install = subparsers.add_parser('install')
  install.add_argument('name')
  install.set_defaults(func=install_module)

  args = parser.parse_args()
  if 'func' in args:
    args.func(args)
  else:
  	parser.print_usage()