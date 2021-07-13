# bugfixer-testbench

## Installation
0. Checkout & build
```
git clone --recursive https://github.com/program-repair-project/bugfixer-testbench.git
make
```
Currently `make` only builds `bug-localizer`.
Ignore warnings like
```
warning: Using 'getservbyport' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
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
## Launch a ManyBugs docker
For example,
```
./bin/run-docker.py gzip-2009-09-26-a1d3d4019d-f17cbd13a1  --rm
```
The argument `--rm` is used to delete the docker container automatically after it terminates.

In the docker container, directory `/bugfixer` contains
- `localizer`: directory for localizer
- `synthesizer`: directory for synthesizer
- `bug_desc.json`: bug description

## Run the bug localizer
In the docker container, the following command runs the localizer:
```
/bugfixer/localizer/main.exe .
```
The result is a sorted list of suspicious lines that will be stored in `localizer-out/result.txt`.
Option `-skip_compile` will skip recompilation.
```
/bugfixer/localizer/main.exe -skip_compile . 
```
