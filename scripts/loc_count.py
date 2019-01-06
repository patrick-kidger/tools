import argparse

from ..src import counter


parser = argparse.ArgumentParser(description='Count the lines of Python code in this or another directory.',
                                 epilog='If the -n flag is passed and the -p is not then it will merely print a '
                                        'summary of the current folder. (Excluding subfolders if -u is also passed.)')
parser.add_argument('folder_path', metavar='folder-path', nargs='?', default='.', help='The path to the folder to count'
                                                                                       ' in. Defaults to the current '
                                                                                       'folder.')
parser.add_argument('-i', '--hidden-files', action='store_true', help='Count hidden files.')
parser.add_argument('-o', '--hidden-folders', action='store_true', help='Count hidden folders.')
parser.add_argument('-p', '--print-files', action='store_true', help='Print counts for each file.')
parser.add_argument('-n', '--no-print-folders', action='store_false', help="Don't print counts for each folder.")
parser.add_argument('-z', '--include-zero', action='store_true', help='Print out lines for files and folders with zero '
                                                                      'lines of code.')
parser.add_argument('-u', '--no-add-subfolders', action='store_false', help="Don't include the lines of code in "
                                                                            "subfolders when summing the total lines of"
                                                                            " code in a folder.")
args = parser.parse_args()
counter.loc_count(args.folder_path, hidden_files=args.hidden_files, hidden_folders=args.hidden_folders,
                  print_files=args.print_files, print_folders=args.no_print_folders, include_zero=args.include_zero,
                  add_subfolders=args.no_add_subfolders)
