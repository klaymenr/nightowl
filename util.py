import argparse
import os
import ConfigParser


def parse_argument():
    parser = argparse.ArgumentParser(description="Grabber - Download snapshots with IR switching")
    parser.add_argument("IP", help="Remote IP", type=str, metavar="IP", nargs="?", default='192.168.1.20')
    parser.add_argument("-u", "--username", help="Username", type=str, default='ubnt')
    parser.add_argument("-p", "--password", help="Password", type=str, default='ubnt')
    parser.add_argument("-i", "--iterations", help="iterations to run", type=int, default=5000)
    parser.add_argument('-o', "--outputdir", help="Folder to store snapshots", type=str, default='grabbed_images')

    return parser


def ParsingArguments():
    parser = parse_argument()
    args = parser.parse_args()

    config_file = 'grabber.ini'
    configs = {}
    if os.path.isfile(config_file):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)
        configs['ip'] = config_parser.get('camera', 'ip')
        configs['username'] = config_parser.get('camera', 'username')
        configs['password'] = config_parser.get('camera', 'password')
        configs['iteritems'] = config_parser.get('test', 'iterations')
        configs['output'] = config_parser.get('test', 'output')

    cliargs = {}
    cliargs['ip'] = args.IP
    cliargs['username'] = args.username
    cliargs['password'] = args.password
    cliargs['iterations'] = args.iterations
    cliargs['outputdir'] = args.outputdir

    final_config = configs if configs else cliargs
    return final_config
