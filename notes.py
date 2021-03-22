from argparse import ArgumentParser
from datetime import datetime
from getpass import getuser
from os import path, startfile
from re import match
from shutil import copy2

import colorama
colorama.init(convert=True)#windows specific?

init_file = r"C:\Users\{}\apps\notes_init.ini".format(getuser())
redundancy_path = r"C:\Users\{}\apps\redundancy.txt".format(getuser())

version = 0.3

def ensure_redundancy(path_redundant, path_notes):
    if path.isfile(path_redundant):#keep a note archive file in case something happens to main notes file
        with open(path_redundant, 'r') as f:
            redundant_lines = f.readlines()
    else:
        redundant_lines = []
    if path.isfile(path_notes):
        with open(path_notes, 'r') as f:
            these_lines = f.readlines()
    else:
        these_lines = []
    for this_line in these_lines:
        for redundant_line in redundant_lines:
            if this_line.split('--')[0] in redundant_line:
                break
        else:
            redundant_lines.append(this_line)
    with open(path_redundant, 'w') as f:
        f.writelines(redundant_lines)

def get_attr_by_flag_n(args, d, flag_key, n=-1):
    return getattr(args, d.get(flag_key)[n].strip())

def main():
    
    d, args = process_init()
    
    user_file_path = get_attr_by_flag_n(args, d, "default_defaultfile_flags")
    default_file_path = get_attr_by_flag_n(args, d, "default_changefilename_flags")
    open_default_file = get_attr_by_flag_n(args, d, "default_open_flags")
    initiate_loop = get_attr_by_flag_n(args, d, "default_loop_flags")
    topics = get_attr_by_flag_n(args, d, "default_topic_flags")#could be None or list of passed in topics
    
    # user_file_path = getattr(args, d.get("default_defaultfile_flags")[-1].strip())
    
    # default_file_path = getattr(args, d.get("default_changefilename_flags")[-1].strip())
    
    # open_default_file = getattr(args, d.get("default_open_flags")[-1].strip())
    
    # initiate_loop = getattr(args, d.get("default_loop_flags")[-1].strip())
    
    this_version = getattr(args, "version")
    
    ensure_redundancy(redundancy_path, default_file_path)

    if open_default_file is True:##launch default file
        if path.isfile(d.get('default_file')):
            print('Opening {}'.format(d.get('default_file')))
            startfile("{}".format(d.get('default_file')))
        else:
            print(f'{d.get("default_file")} not found.')
        return
        
    if this_version is True:##display version for user
        print('Notes > Memory, version:{}'.format(version))
        return
    
    if (user_file_path) != d['default_file']:##user changing defaultfile; update init_file
        with open(init_file, 'r') as f:
            lines = f.readlines()
        new_init_file = [i if 'default_file' not in i else 'default_file={}\n'.format((user_file_path)) for i in lines]

        try:
            copy2(init_file, path.join(path.split(init_file)[0], f'COPY - {path.split(init_file)[1]}'))
        except FileNotFoundError:
            print(f'Creating {init_file}')

        with open(init_file, 'w') as f:
            f.writelines(new_init_file)

        print('Default file changed to {}'.format(user_file_path))
        return
    
    if initiate_loop is True:##user entering note-taking loop
        process_loop(args, init_dict=d)
        return

    if (getattr(args, d.get("default_note_flags")[-1].strip())) is None:##no note means user wants note output
        try:
            with open((default_file_path), 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f'\n\tNo such file or directory: {(default_file_path)}\n\t>>Add notes to file before using topic tag.')
            return

        if topics is None:
            for line in lines:
                process_line(line, d)
            return
        for topic in topics:
            print(topic)
            if topic in ['ALL', 'SHOW', 'HELP', 'TOPICS']:
                topics.remove(topic)
                ticker_set = set()
                for line in lines:
                    mat = match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}--(.*?):', line)
                    group = mat.group(1)
                    if len(group) > 0:
                        ticker_set.add(group.upper())
                print('\n  Current Topics in {}'.format(default_file_path) + colorama.Fore.MAGENTA + ':\n\t{}'.format("\n\t".join(list(ticker_set))))
        # if topics[0] in ['ALL', 'SHOW', 'HELP', 'TOPICS']:
        #     ticker_set = set()
        #     for line in lines:
        #         mat = match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}--(.*?):', line)
        #         group = mat.group(1)
        #         if len(group) > 0:
        #             ticker_set.add(group.upper())
        #     print('\n  Current Topics in {}'.format(default_file_path) + colorama.Fore.MAGENTA   + ':\n\t{}'.format("\n\t".join(list(ticker_set))))
            # return

        for line in lines:
            if sum([1 for t in topics if t in line.split('::')[0]]) > 0:
                process_line(line, d)
        return
    
    note_str = ' '.join((getattr(args, d.get("default_note_flags")[-1].strip())))##(getattr(args, d.get("default_note_flags")[-1].strip())) comes in as a list; convert to string
    
    try:##read current notes file content
        with open((default_file_path), 'r') as f:
            string = f.read()
    except FileNotFoundError:
        string = ''

    try:##redundancy to preserve notes
        copy2((default_file_path), f'COPY - {(default_file_path)}')
    except FileNotFoundError:
        print(f'Creating {(default_file_path)}')
    for topic in topics:
        if topic in ['ALL', 'SHOW', 'HELP', 'TOPICS']:
            topics.remove(topic)
            ticker_set = set()
            try:
                with open((default_file_path), 'r') as f:
                    lines = f.readlines()
            except FileNotFoundError:
                print(f'\n\tNo such file or directory: {(default_file_path)}\n\t>>Add notes to file before using topic tag.')
            for line in lines:
                mat = match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}--(.*?):', line)
                group = mat.group(1)
                if len(group) > 0:
                    ticker_set.add(group.upper())
            print('\n  Current Topics in {}:'.format(default_file_path) + colorama.Fore.MAGENTA + '\n\t{}'.format("\n\t".join(list(ticker_set))) + colorama.Fore.WHITE)
    with open((default_file_path), 'w') as f:#if we got this far, we want to write notes to file
        this_note = str(datetime.today())[:19] + '--misc::' + note_str if topics is None else \
            str(datetime.today())[:19] + '--' + ', '.join(topics) + '::' + note_str
        if topics is None:
            f.write(this_note + '\n' + string)
        else:
            f.write(this_note + '\n' + string)
    process_line(this_note, d)

def process_line(line, d):
    line = line.replace(r"\;", r"~~")
    fmtline1 = '--Categories: '.join(line.strip().split('--'))
    fmtline2 = [fmtline1.split('::')[0].upper()] + [i.strip() for i in fmtline1.split('::')[1].split(d.get("default_linebreak", ";"))]
    fmtline2 = [i.replace("~~", ";") for i in fmtline2]
    print(colorama.Back.BLACK, end='')##print it pretty
    for l in fmtline2:
        if '--CATEGORIES' in l:
            print(colorama.Fore.CYAN + f'\n {l.split("--")[0]}' + colorama.Fore.WHITE)
            print(colorama.Fore.MAGENTA + f'  {l.split("--")[1][:11]}' + colorama.Fore.WHITE)
            for i, cat in enumerate(l.split("--")[1][11:].split(',')):
                if i % 4 == 0 and i != 0:
                    nlc = '\n'
                elif i == len(l.split("--")[1][11:].split(',')) - 1:
                    nlc = '\n'
                else:
                    nlc = ','
                print(f'   {cat}', end=nlc)
            print(colorama.Fore.MAGENTA + '  NOTES:' + colorama.Fore.WHITE)
        else:
            if len(l) != 0:
                l = l.replace("<code>", colorama.Fore.GREEN)\
                    .replace("</code>", colorama.Fore.LIGHTWHITE_EX)\
                    .replace("<h>", colorama.Fore.YELLOW)\
                    .replace("</h>", colorama.Back.RESET + colorama.Fore.LIGHTWHITE_EX)\
                    .replace(">>>", colorama.Fore.GREEN + ">>>").replace("<<<", colorama.Fore.LIGHTWHITE_EX)
                    # .replace("<h>", colorama.Back.MAGENTA + colorama.Fore.WHITE)\
                    # .replace("</h>", colorama.Fore.LIGHTWHITE_EX)
                # colorama.Fore.
                print(
                    colorama.Fore.CYAN + \
                    '    >>' + \
                    colorama.Fore.LIGHTWHITE_EX + \
                    f'\t{l}'
                    )
    print(colorama.Fore.RESET + colorama.Back.RESET)##back to basics


def process_loop(args, init_dict={}):
    # d = init_dict
    print(##loop instructions
        'Initiating loop. \n\tType "-e" or "--exit" to break out of loop at any time.\n\t'\
        'Type "-s" when specifying topics to keep previous topics.\n\t'\
        f'Denote line breaks with "{init_dict.get("default_linebreak", ";")}" when typing notes.\n'
    )
    if path.isfile((getattr(args, init_dict.get("default_changefilename_flags")[-1].strip()))):##grab most recent topics on file
        with open((getattr(args, init_dict.get("default_changefilename_flags")[-1].strip())), 'r', encoding='latin1') as f:
            line = f.readline()
        mat = match(r'^.*--(.*)::', line)
        user_topics = mat.group(1) if mat else 'misc'
    else:
        user_topics = 'misc'
    while True:##enter loop and take notes until user breaks out
        user_input = input(f'Enter comma-separated topics. Previous Topics: {user_topics}\n\t')
        if user_input == '-e' or user_input == '--exit':
            break
        if user_input != '-s':
            user_topics = user_input if user_input != '' else 'misc'
        user_input = input(f'Enter Note (separate thoughts denoted by {init_dict.get("default_linebreak", ";")}):\n\t')
        if user_input == '-e' or user_input == '--exit':
            break
        try:
            with open((getattr(args, init_dict.get("default_changefilename_flags")[-1].strip())), 'r') as f:
                string = f.read()
        except FileNotFoundError:
            string = ''

        try:
            copy2((getattr(args, init_dict.get("default_changefilename_flags")[-1].strip())), f'COPY - {(getattr(args, init_dict.get("default_changefilename_flags")[-1].strip()))}')
        except FileNotFoundError:
            print(f'Creating {(getattr(args, init_dict.get("default_changefilename_flags")[-1].strip()))}')

        with open((getattr(args, init_dict.get("default_changefilename_flags")[-1].strip())), 'w') as f:
            f.write(str(datetime.today())[:19] + '--' + user_topics + '::' + user_input + '\n' + string)

        process_line(str(datetime.today())[:19] + '--' + user_topics + '::' + user_input, init_dict)#pretty print thoughts as they're typed

def init_args(d):

    parser = ArgumentParser(
        prog='Notes > Memory', 
        description='Never rely on memory; type it out!', 
        epilog='Now take notes!'
    )
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-v', '--version', action='store_true', 
        help='show software version and exit'
        )
    group.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_open_flags",
                ["o", 'openfile']
                )
        ], 
        action='store_true', 
        help='launch notes text file (currently {}) and exit'.format(d.get('default_file'))
        )
    group.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_defaultfile_flags",
                ["d", "defaultfile", "default"]
                )
        ],
        help='change default file name where notes should be stored '\
            f'(i.e.: {d.get("default_file")}) and exit', 
            default=d.get('default_file')
        )
    group.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_loop_flags",
                ["l", "loop"]
                )
        ], 
        action='store_true', 
        help='initiate note-taking loop - - - - - - - - - - - - - - '\
            'best for multiple notes back to back - - - - - - - - - '\
            'to exit, type and enter "--exit" or "-e" at any time - '\
            'when specifying topics, "-s" to keep previous topics'
        )
    parser.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_note_flags",
                ["a", "n", "note"]
                )
        ], 
        nargs='+', 
        help='add note to file; '\
            f'specify topic with -{str([i for i in d.get("default_topic_flags", ["t"]) if len(i) == 1])} flag(s) '\
            f'specify file name with -{str([i for i in d.get("default_changefilename_flags", ["f"]) if len(i) == 1])} flag(s) - - - - - - - - '\
            f'(default: ./{d.get("default_file")}) - - - - - - - - - - - - - - - - - - - - - - - - - - - WARNING - - - - - - - - - - - this flag does NOT like the & character; it works just fine in the loop though'
        )
    parser.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_changefilename_flags",
                ["f", "filename"]
                )
        ], 
        help='specify file name where this note should be stored (default file remains {})'.format(d.get('default_file')), default=d.get('default_file')
        )
    parser.add_argument(
        *[
            f'-{flag.strip()}' 
            if len(flag.strip()) == 1 
            else f'--{flag.strip()}' 
            for flag in d.get(
                "default_topic_flags",
                ["t", "topic"]
                )
        ],
        nargs='+', 
        help=f'specify one or more topics of interest to attached to '\
            f'note being added - - - - - - - - - - - - - - - - - - - execute alone to output notes associated with entered '\
            f'flag(s); execute flag -{str(d.get("default_topic_flags", "t"))} ALL to see all current topics in {d.get("default_file")}'
        )
    return parser

def process_init():
    
    d = {}
    
    d["default_file"] = "mynotes.txt"
    d["default_linebreak"] = ";"
    d["default_open_flags"] = ["o", "openfile"]
    d["default_defaultfile_flags"] = ["d", "defaultfile"]
    d["default_loop_flags"] = ["l", "loop"]
    d["default_note_flags"] = ["n", "a", "note"]
    d["default_changefilename_flags"] = ["f", "filename"]
    d["default_topic_flags"] = ["t", "topic"]

    if path.isfile(init_file):##process init_file indicated above if exists
        with open(init_file, 'r') as f:
            init_lines = f.readlines()
        for line in init_lines:#process data and overwrite dict if data present; o/w goes with defaults
            for k in d:
                if k in line:
                    if ',' in line:#comma means list
                        d[k] = line.strip()\
                            .split('=')[1]\
                            .split(',')
                    else:
                        d[k] = line.strip().split('=')[1]
    else:##init_file not existing; create and initialize defaults
        with open(init_file, 'w') as f:#defaults from dictionary above
            for k, v in d.items():
                if type(v) == list:
                    f.write(f'{k}={",".join(v)}\n')
                else:
                    f.write(f'{k}={v}\n')
        
    parser = init_args(d)
    
    args = parser.parse_args()
    
    return d, args

# def init_args(d):

#     parser = ArgumentParser(
#         prog='NotesOverMemory', 
#         description='Never rely on memory; type it out!', 
#         epilog='Now take notes!'
#     )
#     group = parser.add_mutually_exclusive_group()

#     group.add_argument(
#         '-v', '--version', action='store_true', 
#         help='show software version and exit'
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_open_flags", ["o"])], '--openfile', action='store_true', 
#         help='launch notes text file (currently {}) and exit'.format(d.get('default_file'))
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_defaultfile_flags", ["d"])], '--defaultfile', '--default', 
#         help='change default file name where notes should be stored '\
#             f'(i.e.: {d.get("default_file")}) and exit', 
#             default=d.get('default_file')
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_loop_flags", ["l"])], '--loop', action='store_true', 
#         help='initiate note-taking loop - - - - - - - - - - - - - - '\
#             'best for multiple notes back to back - - - - - - - - - '\
#             'to exit, type and enter "--exit" or "-e" at any time - '\
#             'when specifying topics, "-s" to keep previous topics'
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_note_flags", ["a", "n"])], '--note', nargs='+', 
#         help='add note to file; '\
#             f'specify topic with -{str(d.get("default_topic_flags", "t"))} flag(s) '\
#             f'specify file name with -{str(d.get("default_changefilename_flags", "f"))} flag(s) - - - - - - - - '\
#             f'(default: ./{d.get("default_file")}) - - - - - - - - - - - - - - - - - - - - - - - - - - - WARNING - - - - - - - - - - - this flag does NOT like the & character; it works just fine in the loop though'
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_changefilename_flags", ["f"])], '--filename', '--file', 
#         help='specify file name where this note should be stored (currently {})'.format(d.get('default_file')), default=d.get('default_file')
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_topic_flags", ["t"])], '--topic', nargs='+', 
#         help=f'specify one or more topics of interest to attached to '\
#             f'note being added - - - - - - - - - - - - - - - - - - - execute alone to output notes associated with entered '\
#             f'flag(s); execute flag -{str(d.get("default_topic_flags", "t"))} ALL to see all current topics in {d.get("default_file")}'
#         )
#     return parser
    
if __name__ == '__main__':
    main()

# from argparse import ArgumentParser
# from datetime import datetime
# from getpass import getuser
# from os import path, startfile
# from re import match
# from shutil import copy2

# import colorama
# colorama.init(convert=True)#windows specific?

# '''Version 0.2'''

# init_file = r"C:\Users\{}\notes_init.ini".format(getuser())

# version = 0.1

# def main():
#     d = {}
#     if path.isfile(init_file):##process init_file indicated above if exists
#         with open(init_file, 'r') as f:
#             init_lines = f.readlines()
#         for line in init_lines:
#             if 'default_file' in line:
#                 d['default_file'] = line.strip().split('=')[1]
#             if 'default_linebreak' in line:
#                 d['default_linebreak'] = line.strip().split('=')[1]
#             if 'default_open_flags' in line:
#                 d['default_open_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#             if 'default_defaultfile_flags' in line:
#                 d['default_defaultfile_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#             if 'default_loop_flags' in line:
#                 d['default_loop_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#             if 'default_note_flags' in line:
#                 d['default_note_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#             if 'default_changefilename_flags' in line:
#                 d['default_changefilename_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#             if 'default_topic_flags' in line:
#                 d['default_topic_flags'] = line.strip()\
#                     .split('=')[1]\
#                     .split(',')
#     else:##init_file not existing; create and initialize defaults
#         with open(init_file, 'w') as f:
#             f.write(
#                 'default_file=mynotes.txt\n'\
#                 'default_linebreak=;\n'\
#                 'default_open_flags=o\n'\
#                 'default_defaultfile_flags=d\n'\
#                 'default_loop_flags=l\n'\
#                 'default_note_flags=n, a\n'\
#                 'default_changefilename_flags=f\n'\
#                 'default_topic_flags=t\n'
#                 )
#         d['default_file'] = 'notes.txt'
#         d['default_linebreak']=";"
#         d['default_open_flags']=["o"]
#         d['default_defaultfile_flags']=["d"]
#         d['default_loop_flags']=["l"]
#         d['default_note_flags']=["n", "a"]
#         d['default_changefilename_flags']=["f"]
#         d['default_topic_flags']=["t"]
            
#     parser = init_args(d)
    
#     args = parser.parse_args()

#     if path.isfile(path):
#         with open(path, 'r') as f:
#             redundant_lines = f.readlines()
#     else:
#         redundant_lines = []
#     if path.isfile(args.filename):
#         with open(args.filename, 'r') as f:
#             these_lines = f.readlines()
#     else:
#         these_lines = []
#     for this_line in these_lines:
#         for redundant_line in redundant_lines:
#             if this_line.split('--')[0] in redundant_line:
#                 break
#         else:
#             redundant_lines.append(this_line)
#         # if this_line not in redundant_lines:
#         #     redundant_lines.append(this_line)
#     with open(path, 'w') as f:
#         f.writelines(redundant_lines)

#     if args.openfile:##launch default file
#         if path.isfile(d.get('default_file')):
#             print('Opening {}'.format(d.get('default_file')))
#             startfile("{}".format(d.get('default_file')))
#         else:
#             print(f'{d.get("default_file")} not found.')
#         return
        
#     if args.version:##display version for user
#         print('NotesOverMemory, version:{}'.format(version))
#         return
    
#     if args.defaultfile != d['default_file']:##user changing defaultfile; update init_file
#         with open(init_file, 'r') as f:
#             lines = f.readlines()
#         new_init_file = [i if 'default_file' not in i else 'default_file={}\n'.format(args.defaultfile) for i in lines]

#         try:
#             copy2(init_file, path.join(path.split(init_file)[0], f'COPY - {path.split(init_file)[1]}'))
#         except FileNotFoundError as e:
#             print(f'Creating {init_file}')

#         with open(init_file, 'w') as f:
#             f.writelines(new_init_file)

#         print('Default file changed to {}'.format(args.defaultfile))
#         return
    
#     if args.loop:##user entering note-taking loop
#         process_loop(args, init_dict=d)
#         return

#     if args.note is None:##no note means user wants note output
#         try:
#             with open(args.filename, 'r') as f:
#                 lines = f.readlines()
#         except FileNotFoundError as e:
#             print(f'\n\tNo such file or directory: {args.filename}\n\t>>Add notes to file before using ticker tag.')
#             return

#         if args.topic is None:
#             for line in lines:
#                 process_line(line, d)
#             return

#         if args.topic[0] in ['ALL', 'SHOW', 'HELP', 'TOPICS']:
#             ticker_set = set()
#             for line in lines:
#                 mat = match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}--(.*?):', line)
#                 group = mat.group(1)
#                 if len(group) > 0:
#                     ticker_set.add(group.upper())
#             print('\n  Current Topics in {}'.format(arg.f+ ' colorama.Fore.MAGENTA   + :\n\t{}'.format(ename, "\n\t".join(list(ticker_set))))
#             return

#         for line in lines:
#             if sum([1 for t in args.topic if t in line.split('::')[0]]) > 0:
#                 process_line(line, d)
#         return
    
#     note_str = ' '.join(args.note)##args.note comes in as a list; convert to string
    
#     try:##read current notes file content
#         with open(args.filename, 'r') as f:
#             string = f.read()
#     except FileNotFoundError:
#         string = ''

#     try:##redundancy to preserve notes
#         copy2(args.filename, f'COPY - {args.filename}')
#     except FileNotFoundError as e:
#         print(f'Creating {args.filename}')

#     with open(args.filename, 'w') as f:#if we got this far, we want to write notes to file
#         if args.topic is None:
#             f.write(str(datetime.today())[:19] + '--misc::' + note_str + '\n' + string)
#         else:
#             f.write(str(datetime.today())[:19] + '--' + ', '.join(args.topic) + '::' + note_str + '\n' + string)

# def process_line(line, d):

#     fmtline1 = '--Categories: '.join(line.strip().split('--'))
#     fmtline2 = [fmtline1.split('::')[0].upper()] + [i.strip() for i in fmtline1.split('::')[1].split(d.get("default_linebreak", ";"))]

#     print(colorama.Back.BLACK, end='')##print it pretty
#     for l in fmtline2:
#         if '--CATEGORIES' in l:
#             print(colorama.Fore.CYAN + f'\n {l.split("--")[0]}' + colorama.Fore.WHITE)
#             print(colorama.Fore.MAGENTA + f'  {l.split("--")[1][:11]}' + colorama.Fore.WHITE)
#             for i, cat in enumerate(l.split("--")[1][11:].split(',')):
#                 if i % 4 == 0 and i != 0:
#                     nlc = '\n'
#                 elif i == len(l.split("--")[1][11:].split(',')) - 1:
#                     nlc = '\n'
#                 else:
#                     nlc = ','
#                 print(f'   {cat}', end=nlc)
#             print(colorama.Fore.MAGENTA + '  NOTES:' + colorama.Fore.WHITE)
#         else:
#             if len(l) != 0:
#                 print(colorama.Fore.CYAN + '    >>' + colorama.Fore.LIGHTWHITE_EX + f'\t{l}')
#     print(colorama.Fore.RESET + colorama.Back.RESET)##back to basics


# def process_loop(args, init_dict={}):
#     print(##loop instructions
#         'Initiating loop. \n\tType "-e" or "--exit" to break out of loop at any time.\n\t'\
#         'Type "-s" when specifying topics to keep previous topics.\n\t'\
#         f'Denote line breaks with "{init_dict.get("default_linebreak", ";")}" when typing notes.\n'
#     )
#     if path.isfile(args.filename):##grab most recent topics on file
#         with open(args.filename, 'r', encoding='latin1') as f:
#             line = f.readline()
#         mat = match(r'^.*--(.*)::', line)
#         user_topics = mat.group(1) if mat else 'misc'
#     else:
#         user_topics = 'misc'
#     while True:##enter loop and take notes until user breaks out
#         user_input = input(f'Enter comma-separated topics. Previous Topics: {user_topics}\n\t')
#         if user_input == '-e' or user_input == '--exit':
#             break
#         if user_input != '-s':
#             user_topics = user_input if user_input != '' else 'misc'
#         user_input = input(f'Enter Note (separate thoughts denoted by {init_dict.get("default_linebreak", ";")}):\n\t')
#         if user_input == '-e' or user_input == '--exit':
#             break
#         try:
#             with open(args.filename, 'r') as f:
#                 string = f.read()
#         except FileNotFoundError:
#             string = ''

#         try:
#             copy2(args.filename, f'COPY - {args.filename}')
#         except FileNotFoundError as e:
#             print(f'Creating {args.filename}')

#         with open(args.filename, 'w') as f:
#             f.write(str(datetime.today())[:19] + '--' + user_topics + '::' + user_input + '\n' + string)


# def init_args(d):

#     parser = ArgumentParser(
#         prog='NotesOverMemory', 
#         description='Never rely on memory; type it out!', 
#         epilog='Now take notes!'
#     )
#     group = parser.add_mutually_exclusive_group()

#     group.add_argument(
#         '-v', '--version', action='store_true', 
#         help='show software version and exit'
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_open_flags", ["o"])], '--openfile', action='store_true', 
#         help='launch notes text file (currently {}) and exit'.format(d.get('default_file'))
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_defaultfile_flags", ["d"])], '--defaultfile', '--default', 
#         help='change default file name where notes should be stored '\
#             f'(i.e.: {d.get("default_file")}) and exit', 
#             default=d.get('default_file')
#         )
#     group.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_loop_flags", ["l"])], '--loop', action='store_true', 
#         help='initiate note-taking loop - - - - - - - - - - - - - - '\
#             'best for multiple notes back to back - - - - - - - - - '\
#             'to exit, type and enter "--exit" or "-e" at any time - '\
#             'when specifying topics, "-s" to keep previous topics'
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_note_flags", ["a", "n"])], '--note', nargs='+', 
#         help='add note to file; '\
#             f'specify topic with -{str(d.get("default_topic_flags", "t"))} flag(s) '\
#             f'specify file name with -{str(d.get("default_changefilename_flags", "f"))} flag(s) - - - - - - - - '\
#             f'(default: ./{d.get("default_file")}) - - - - - - - - - - - - - - - - - - - - - - - - - - - WARNING - - - - - - - - - - - this flag does NOT like the & character; it works just fine in the loop though'
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_changefilename_flags", ["f"])], '--filename', '--file', 
#         help='specify file name where this note should be stored (currently {})'.format(d.get('default_file')), default=d.get('default_file')
#         )
#     parser.add_argument(
#         *[f'-{flag.strip()}' for flag in d.get("default_topic_flags", ["t"])], '--topic', nargs='+', 
#         help=f'specify one or more topics of interest to attached to '\
#             f'note being added - - - - - - - - - - - - - - - - - - - execute alone to output notes associated with entered '\
#             f'flag(s); execute flag -{str(d.get("default_topic_flags", "t"))} ALL to see all current topics in {d.get("default_file")}'
#         )
#     return parser
    
# if __name__ == '__main__':
#     main()
