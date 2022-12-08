import argparse
import socket
import mcrcon
import re
import os
from time import sleep, time

def process_message(message: str):
    result = ''
    i= 0
    while i < len(message):
        if message[i] == '§':
            i += 2
        else:
            result += message[i]
            i += 1
    return result

def get_tps_from_message(message: str):
    numbers = re.findall(r'\b\d+\.*\d*\b', message)
    mspt = numbers[3]
    return mspt

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("password")
    args = parser.parse_args()

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))

    with open("tps.txt", "w+") as file:
        
        file.write("\t".join(["timestamp", "tps"]))
        file.write(os.linesep)
        file.flush()
        try:
            # Log in
            result = mcrcon.login(sock, args.password)
            if not result:
                print("Incorrect rcon password")
                return

            # Start looping
            while True:
                # mcrcon.command(sock, "debug start")
                # sleep(5)
                # response = mcrcon.command(sock, "debug stop")
                # numbers = re.findall(r'\b\d+\.*\d*\b', response)
                # seconds = float(numbers[0])
                # ticks = int(numbers[1])
                # tps = int(ticks / seconds)
                # file.write(f"{time() * 1000}\t{tps}")
                # file.write(os.linesep)
                # file.flush()
                response = mcrcon.command(sock, "mspt")
                cleaned_response = process_message(response)
                mspt = get_tps_from_message(cleaned_response)
                file.write(f"{time() * 1000}\t{mspt}")
                file.write(os.linesep)
                file.flush()
                sleep(1)
                
        finally:
            sock.close()

if __name__ == '__main__':
    main()
