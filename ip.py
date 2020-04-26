import subprocess


def get_host_ip() -> str:
    process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', 'inet 192'), stdin=process.stdout)
    process.wait()
    output = str(output).strip()
    comp = output.split(' ')
    for i in range(len(comp)):
        if comp[i] == 'inet':
            return comp[i + 1]

    return ""
