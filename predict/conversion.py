import subprocess

def convert_to_wav(fullpathin):
    cmd = ["ffmpeg","-y", "-i", (fullpathin), fullpathin[:-4] + ".wav"]
    print(cmd)
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
