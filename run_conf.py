from pyhocon import ConfigFactory
from pprint import pprint
from pyhocon.converter import HOCONConverter
import subprocess
import os
from time import sleep


game_address = "34.152.28.197"
game_port = "25565"


def run_tmp_config(conf):
    tmp_config = 'tmp_config.conf'
    with open(tmp_config, "w") as fd:
        fd.write(HOCONConverter.to_hocon(conf))

    subprocess.run([f"java -Dconfig.file={tmp_config} -Xms64G -Xmx64G -jar yardstick.jar --address {game_address}:{game_port} --nodeID 0"], shell=True)
    
    os.remove(tmp_config)


def run_experiment_with_static_bot():
    experiment = '11'
    conf = ConfigFactory.parse_file('./application.conf')
    conf['yardstick']['player-emulation']['arguments']['behavior']['name'] = experiment

    run_tmp_config(conf)

def run_experiment_with_increasing_bot():

    experiment = '13'

    conf = ConfigFactory.parse_file('./application.conf')

    conf['yardstick']['player-emulation']['arguments']['behavior']['name'] = experiment
    conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['bots'] = 300
    conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['duration'] = "60000s"
    conf['yardstick']['player-emulation']['arguments']['duration'] = "60000s"

    conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['joininterval'] = "1s"
    conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['numbotsperjoin'] = 1

    run_tmp_config(conf)

def run_experiment_with_different_number_of_bots():
    conf = ConfigFactory.parse_file('./application.conf')
    # bots_numbers = [25, 50, 75, 100, 125, 150]
    bots_numbers = [50]
    experiment = '8'

    for bots_number in bots_numbers:

        conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['bots'] = bots_number
        conf['yardstick']['player-emulation']['arguments']['behavior'][experiment]['duration'] = "60000s"
        conf['yardstick']['player-emulation']['arguments']['duration'] = "60000s"

        run_tmp_config(conf)

        sleep(10)

def main():
    run_experiment_with_increasing_bot()

if __name__ == '__main__':
    main()