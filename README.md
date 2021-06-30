# bugfixer-testbench

## Instruction
0. Checkout
```
git clone --recursive https://github.com/program-repair-project/bugfixer-testbench.git
```

1. Install [Bugzoo](https://github.com/squaresLab/BugZoo)
```
pipenv install bugzoo
```

2. Build ManyBugs dockers
For example,
```
bugzoo bug build manybugs:gzip:2009-08-16-3fe0caeada-39a362ae9d
```

3. Launch a ManyBugs docker
For example,
```
./bin/run-docker.py gzip-2009-09-26-a1d3d4019d-f17cbd13a1  --rm
```
The argument `--rm` is used to delete the docker container automatically after it terminates.
