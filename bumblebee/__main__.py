import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="BotQueue's client bumblebee")

    command_parser = parser.add_subparsers(dest="command", help='command help')

    parser_config = command_parser.add_parser('config', help='Configuration control')
    parser_config.add_argument("--server", help="Change config to use a different server")

    if len(sys.argv) == 1:
        from .app import main
        main()
        return

    args = parser.parse_args()

    # Figure out how to actually follow the log
    if args.command == "log":
        from bumblebee.hive import getLogPath
        print getLogPath()

    if args.command == "config":
        import hashlib
        import time

        from bumblebee.bee_config import BeeConfig

        config = BeeConfig()
        if args.server is not None:
            url = args.server
            if url[-1:] == '/':
                url = url[:-1]

            consumer_key = raw_input("Consumer Key: ")
            consumer_secret = raw_input("Consumer Secret: ")

            config['app_url'] = url
            config['api']['authorize_url'] = url + '/app/authorize'
            config['api']['endpoint_url'] = url + '/api/v1/endpoint'
            config['app']['consumer_key'] = consumer_key
            config['app']['consumer_secret'] = consumer_secret

            if 'uid' not in config or not config['uid']:
                config['uid'] = hashlib.sha1(str(time.time())).hexdigest()

            config.save()

            print "Now you can run the client to register"
        else:
            print "App url: %s" % config['app_url']
            print "Consumer key: %s" % config['app']['consumer_key']
            if 'token_key' in config['app'] and config['app']['token_key']:
                print "Token key: %s" % config['app']['token_key']
                print "App has been registered"
            else:
                print "App has not been registered yet"


if __name__ == "__main__":
    main()
