# bugfixer-testbench

## Installation
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
## Run with Docker Images
1. Launch a ManyBugs docker
For example,
```
./bin/run-docker.py gzip-2009-09-26-a1d3d4019d-f17cbd13a1  --rm
```
The argument `--rm` is used to delete the docker container automatically after it terminates.

In the docker container, directory `/bugfixer` contains
- `localizer`: directory for localizer
- `synthesizer`: directory for synthesizer
- `bug_desc.json`: bug description

2. Run the localizer
In the docker container, the following command runs the localizer:
```
/bugfixer/localizer/main.exe .
```
The result is a sorted list of suspicious lines that will be stored in `localizer-out/result.txt`.
