import argparse
from argparse import Action

def main(**args):
    print args['name']
    other_args = {}
    # if args.name is not None:
    #     other_args['name'] = args.name
    # if args.number is not None:
    #     other_args['number'] = args.number

    if args['name'] is not None:
        other_args['name'] = args['name']
    if args['number'] is not None:
        other_args['number'] = args['number']
    return other_args

def other(name='zstewart', number=1):
    print name, number

class custom_action(argparse.Action):
    print "bingoooooooooo"
    def __call__(self, parser, namespace, values, option_string=None):
        n, v = values
        setattr(namespace, n, v)
        print n,v

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("name",
                        nargs="*"
                        )

    parser.add_argument("-a",
                        "--number",
                        type=int
                        )

    parser.add_argument('-s',
                        '--stats',
                        help = 'c for country or j for geojson',
                        nargs=argparse.REMAINDER
                        ,action=custom_action
                        )

    parser.add_argument('-w', '--multi', action = 'append')

    #parser.add_argument('-k', '--custom', action=custom_action)

    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity",
                        action="store_true")

    params = parser.parse_args()
    print "Parametri", params

    # converted_in_dict = main(params)
    # print "Convertito in Dictionary",converted_in_dict
    # other(**converted_in_dict)

    args_list = {k: v for k, v in vars(params).items() if v is not None}
    print "args", args_list
    converted_in_dict = main(**args_list)
    other(**converted_in_dict)