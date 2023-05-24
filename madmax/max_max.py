import os
import subprocess

PLOT_SIZE=32
TEMP_DIR1="/media/kosios/MPP/chiaTemp/"
TEMP_RAM="/mnt/ram/"
FINAL_DIR="/media/kosios/A1/chiaPoolFinal/"
POOL_CONTRACT_ADDRESS="xch1ajklck738l9j55h9ut8rnvwrh7lps9xqv8gyn4ahw28dxplapscqcqsgsp"
FARM_KEY="a1684ef76aaf3e148dfdddd7d854ab83afd3af6a067c60186312413027201b5d07144f7760c0e3b396a7f98944f9abc3"
NUM_PLOTS=10
NUM_THREADS=32
BUCKETS=512

MOUNT_RAM_COMMAND="sudo mount -t tmpfs -o size=110G tmpfs /mnt/ram/"

MAD_MAX_PATH="/home/kosios/madMax/chia-plotter/build"



def main():
    fullCommand = f"./chia_plot -t {TEMP_DIR1} -2 {TEMP_RAM} -d {FINAL_DIR} -c {POOL_CONTRACT_ADDRESS} -f {FARM_KEY} -n {NUM_PLOTS} -r {NUM_THREADS} -u {BUCKETS}"
    print("Running command: ", fullCommand)
    execute(fullCommand, MAD_MAX_PATH)


def execute(cmd, dir):
    popen = subprocess.Popen(cmd, cwd=dir, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


if __name__ == "__main__":
    main()