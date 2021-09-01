#!/usr/bin/env python3
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('project', type=str)
    args = parser.parse_args()
    p = args.project
    ps_cmd = ['docker', 'ps']
    ps = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
    containers = list(
        map(lambda line: line.split(),
            ps.stdout.split('\n')[1:-1]))
    for c in containers:
        if f'prosyslab/manybugs:{p}' in c[1]:
            stop_cmd = ['docker', 'stop', f'{c[0]}']
            stop = subprocess.run(stop_cmd, check=True)
            rm_cmd = ['docker', 'rm', f'{c[0]}']
            rm = subprocess.run(rm_cmd, check=True)


if __name__ == '__main__':
    main()
