import argparse
import sys

from client import Client
from server import Server

def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--server", help="Create and run a FTP server instance", action="store_true")
    ap.add_argument("-c", "--client", help="Create and run a FTP client instance", action="store_true")
    args = ap.parse_args()

    if args.server:
        # create and run the server
        server = Server()
        server.run_server()

    if args.client:
        # create and run client
        client = Client()
        client.cmdloop()

    if not args.server and not args.client:
        # none specified so exit
        sys.exit("You must specify to start and create either a client or server")


if __name__ == '__main__':
    main()