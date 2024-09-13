# for getDatetime
from dateutil import parser


def get_string(args, query_type):
    args = str(args)
    args_type = ''
    if query_type == 'L' or query_type == 'l' or query_type == 'literal' or query_type == 'LITERAL':
        args_type = 'literal'
    elif query_type == 'B' or query_type == 'b' or query_type == 'bind' or query_type == 'BIND':
        args_type = 'bind'
    else:
        return args

    if args == '' and args_type == 'literal':
        return 'NULL'
    elif args != '' and args_type == 'literal':
        return "'" + args + "'"
    elif args == '' and args_type == 'bind':
        return None
    elif args != '' and args_type == 'bind':
        return args
    else:
        return args


def get_number(args, query_type):
    args_type = ''
    if query_type == 'L' or query_type == 'l' or query_type == 'literal' or query_type == 'LITERAL':
        args_type = 'literal'
    elif query_type == 'B' or query_type == 'b' or query_type == 'bind' or query_type == 'BIND':
        args_type = 'bind'
    else:
        return args

    if args == '' and args_type == 'literal':
        return 'NULL'
    elif args != '' and args_type == 'literal':
        return args
    elif args == '' and args_type == 'bind':
        return None
    elif args != '' and args_type == 'bind' and isinstance(args, int):
        return int(args)
    elif args != '' and args_type == 'bind' and isinstance(args, float):
        return float(args)
    elif args != '' and args_type == 'bind' and isinstance(args, str):
        try:
            return int(args)
        except:
            return float(args)
    else:
        return args


def get_datetime(args, query_type):
    args_type = ''

    if query_type == 'L' or query_type == 'l' or query_type == 'literal' or query_type == 'LITERAL':
        args_type = 'literal'
    elif query_type == 'B' or query_type == 'b' or query_type == 'bind' or query_type == 'BIND':
        args_type = 'bind'
    else:
        return args

    if args == '' and args_type == 'literal':
        return 'NULL'
    elif args != '' and args_type == 'literal':
        return "'" + parser.parse(args).strftime("%Y-%m-%d %H:%M:%S") + "'"
    elif args == '' and args_type == 'bind':
        return None
    elif args != '' and args_type == 'bind':
        return parser.parse(args).isoformat()
    else:
        return args

def get_size_kb_bps(args):
    if 'Mbps'   in args:
        return str(round(float(args.replace("Mbps","").strip())*1024,2))
    elif 'Gbps' in args:
        return str(round(float(args.replace("Gbps","").strip())*1024*1024,2))
    elif 'Tbps' in args:
        return str(round(float(args.replace("Tbps","").strip())*1024*1024*1024,2))
    elif 'Kbps' in args:
        return str(round(float(args.replace("Kbps","").strip())*1,2))
    elif '-'    in args:
        return str('0')
    elif 'bps'  in args:
        return str(round(float(args.replace("bps","").strip())/1024,2))    
    else:
        return args


def get_size_mb(args):
    if 'MB' in args:
        return str(round(float(args.replace("MB","").strip())*1,2))
    elif 'GB' in args:
        return str(round(float(args.replace("GB","").strip())*1024,2))
    elif 'TB' in args:
        return str(round(float(args.replace("TB","").strip())*1024*1024,2))
    elif 'KB' in args:
        return str(round(float(args.replace("KB","").strip())/1024,2))
    else:
        return args

def get_elapsed_sec(args):
    if args == '':
        return 'NULL'
    else: 
        hours = int(args.split(':')[0]) * 3600
        mins  = int(args.split(':')[1]) * 60
        secs  = int(args.split(':')[2])
        return str(hours + mins +secs)