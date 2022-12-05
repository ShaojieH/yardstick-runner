from pyhocon import ConfigFactory
from pprint import pprint
from pyhocon.converter import HOCONConverter
import subprocess
from time import sleep


game_address = "34.118.33.64"
game_port = "25565"



def run_experiment_with_different_number_of_bots():
    conf = ConfigFactory.parse_file('./application.conf')
    bots_numbers = [25, 50, 75, 100, 125, 150]
    # bots_numbers = [1, 2]
    experiment = '8'

    for bots_number in bots_numbers:

        conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['bots'] = bots_number

        tmp_config = 'tmp_config.conf'
        with open(tmp_config, "w") as fd:
            fd.write(HOCONConverter.to_hocon(conf))

        subprocess.run([f"java -Dconfig.file={tmp_config} -Xms16G -Xmx16G -jar yardstick.jar --address {game_address}:{game_port} --nodeID 0"], shell=True)
        sleep(10)

def main():
    run_experiment_with_different_number_of_bots()

if __name__ == '__main__':
    main()