#!/usr/bin/python
import argparse
import re
import subprocess
import sys


class ToolError(Exception):
    def __init__(self, message, exit_code=2):
        super(ToolError, self).__init__(message, exit_code)
        self.message = message
        self.exit_code = exit_code


def get_temps_and_swaps():
    proc = subprocess.run(["/usr/sbin/blkid"], capture_output=True, text=True)
    lines = proc.stdout.split("\n")
    determine_re = re.compile(
        r'^(?P<dev>[^:]+):.*((?P<tmp>LABEL="Temporary Storage".*|TYPE="ntfs".*){2}|(?P<swap>TYPE="swap")).*'
    )
    temps = []
    swaps = []
    for line in lines:
        mo = determine_re.match(line)
        if mo is None:
            pass
        elif mo.group("tmp"):
            temps.append(mo.group("dev"))
        elif mo.group("swap"):
            swaps.append(mo.group("dev"))

    return temps, swaps


def make_swaps(devices):
    ret = []
    dev_re = re.compile(r"^(\D+)\d+$")
    for dev in devices:
        mo = dev_re.match(dev)
        if not mo:
            print(
                "Found temporary drive, expected temporary partition. Skippping",
                dev,
                file=sys.stderr,
            )
            continue
        drive = mo.group(1)
        print("Creating swap on", drive, file=sys.stderr)
        rc = subprocess.run(
            ["/usr/sbin/mkswap", "-L", "Azure Temp", "-f", drive]
        ).returncode
        if rc:
            print("mkswap failed on", drive, file=sys.stderr)
            continue
        subprocess.run(["/usr/sbin/partprobe", drive])
        ret.append(drive)
    return ret


def get_active_swaps():
    with open("/proc/swaps") as f:
        for line in f:
            if line.startswith("/"):
                yield line.split()[0].strip()


def work():
    temps, swaps = get_temps_and_swaps()
    swaps.extend(make_swaps(temps))
    active_swaps = set(get_active_swaps())
    for swap in swaps:
        if swap not in active_swaps:
            print("Activating swap on", swap, file=sys.stderr)
            rc = subprocess.run(["/usr/sbin/swapon", swap]).returncode
            if rc:
                print("swapon failed on", swap, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Format any azure temporary drive as swap and enable it"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        work()
    except ToolError as e:
        print(f"{sys.argv[0]}: error: {e.message}")
        sys.exit(e.exit_code)
    except OSError as e:
        fns = ", ".join([repr(fn) for fn in (e.filename, e.filename2) if fn])
        if fns:
            fns = " " + fns
        print(f"{sys.argv[0]}: error: {e.strerror}" + fns)
        sys.exit(2)


if __name__ == "__main__":
    main()
