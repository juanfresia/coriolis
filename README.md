# CORIOLIS: Rule-based concurrent testing system

![](docs/coriolis_logo.png)

> _Le temps n'est pas éloigné, sans doute, où le travail s'employant davantage, s’économisera mieux, et où l’intérêt qu’on aura à connaître tous ces résultats fera chercher par expérience ceux qui ne peuvent s’obtenir directement par la théorie._

> _The time is not far away, no doubt, where the future work being done, will save itself better, and where the interest which we will have to know all these results will make us search by experience those which can not be obtained directly by theory._


## Abstract

CORIOLIS is a CLI-based framework for running and testing concurrent software. Concurrent test suites are written as [JARL rules](docs/jarl_spec.md), with checkpoints inserted in the code as one-line comments. User's code is executed on a virtualized environment, and the resulting logs from such execution are analyzed for verifying the defined rules.  

## Table of contents

- [CORIOLIS overview](#coriolis-overview)
- [Installation guide](#installation-guide)
  - [Prerequisites](#prerequisites)
  - [Installing from package](#installing-from-package)
  - [Building from source](#building-from-source)
  - [Running from source](#running-from-source)
- [Quick start](#quick-start)
  - [Running Python example](#running-python-example)
  - [Running Rust example](#running-rust-example)
  - [Running C/C++ example](#running-cc-example)
- [Parsing JARL rules](#parsing-jarl-rules)
- [Running user's code](#running-users-code)
- [Verifying JARL rules](#verifying-jarl-rules)

## CORIOLIS overview

CORIOLIS system basically consists of three well-defined parts: 

- A _parser_ which can validate JARL rules and translate them into an internal CORIOLIS representation.
- A _runner_ able to execute the user's code on a virtualized environment, that produces output logs with the execution information.
-  A _verifier_ module that asserts the runner logs are compliant with the parsed rules.

Input files and the relationships between these three parts are summarized on the following image: 

![](docs/coriolis_arch_v2.png)

## Installation guide

The recommended way of using CORIOLIS is downloading and installing its `.deb` package. However, you can still download this repository and either build your own `.deb` package or run CORIOLIS from its source code. 

### Prerequisites

- Ubuntu 16.04 LTS OS
- Docker (check the official docs [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1))

### Installing from package

You can install CORIOLIS from its `.deb` package using `dpkg`:

```
~$ sudo dpkg -i coriolis_1.0_amd64.deb
```

This will add the `coriolis` command to your binaries: 

```
~$ coriolis version
CORIOLIS CLI tool v.1.0
```

Keep in mind that CORIOLIS package will also create a MongoDB service (as it is used for the rules verification) running on port 21592. You can check this service with `systemctl` or `service` using the name `coriolis-mongo`:

```
~$service coriolis-mongo status
● coriolis-mongo.service - MongoDB container for coriolis verifier
   Loaded: loaded (/lib/systemd/system/coriolis-mongo.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2019-11-10 22:48:26 UTC; 15min ago
```

### Building from source

You can build CORIOLIS package from source with the `Makefile` inside the `/coriolis` folder of the repository:

```
~$ make docker-image && make build
docker build -f docker/Dockerfile --build-arg VERSION=1.0-48d972012959-dirty -t coriolis:1.0-48d972012959-dirty .
Sending build context to Docker daemon  41.41MB
Step 1/11 : FROM ubuntu:16.04
...
Successfully tagged coriolis:1.0-48d972012959-dirty
docker run --rm -v /vagrant/coriolis/bin:/mnt coriolis:1.0-48d972012959-dirty bash -c "cp dist/* /mnt"
~$ ls bin/
coriolis_1.0-48d972012959-dirty_amd64.deb
```

### Running from source

Since CORIOLIS is written in Python, you can run it directly from the `coriolis` file inside `/coriolis` folder, just make sure to install all the dependencies inside `requirements.txt`:

```
~$ pip3 install -r requirements.txt
Requirement already satisfied: antlr4-python3-runtime==4.7.2 in /vagrant/venv/lib/python3.5/site-packages (from -r requirements.txt (line 1)) (4.7.2)
...
Requirement already satisfied: websocket-client==0.56.0 in /vagrant/venv/lib/python3.5/site-packages (from -r requirements.txt (line 15)) (0.56.0)
~$ ./coriolis version
CORIOLIS CLI tool v.1.0
```

**Note**: You will still need a MongoDB instance for the rules verification to work.


## Quick start

**Note**: In order for your project to run with CORIOLIS, you must place on it a Bash `run_coriolis.sh` script. Such script should be the responsible for compiling and running your code like you would do it on your machine.

The easiest way to use CORIOLIS is with the basic `coriolis` command. You will want to specify, at least, your source code directory, your JARL rules file, the checkpoints table related to your code, and the language used in your project: 

```
~$ coriolis -s myproject/src -r myrules.jarl -c mycheckpoints.chk -l py
```

**Note**: Remember CORIOLIS uses Docker on the background, so your user must have enough permissions to use the `docker` command.

You can check all flags with `coriolis -h`:

```
~$ coriolis -h
usage: coriolis [-h] [-s source] [-r rules_file] [-c checkpoints]
                [-d destination] [-l language] [-n number] [-t secs]
                [-H mongo_host] [-p mongo_port] [-v] [-C]
                {verify,run,parse} ...

Coriolis CLI tool

positional arguments:
  {verify,run,parse}

optional arguments:
  -h, --help            show this help message and exit
  -s source, --source source
                        Source code directory
  -r rules_file, --rules rules_file
                        Rules .jarl file
  -c checkpoints, --checkpoints checkpoints
                        Checkpoint list file
  -d destination, --destination destination
                        Logs destination directory
  -l language, --language language
                        Source code language
  -n number, --number-runs number
                        Number of runs to perform
  -t secs, --timeout secs
                        Number of seconds to wait before timeout
  -H mongo_host, --mongo-host mongo_host
                        Host or IP of the mongo server
  -p mongo_port, --mongo-port mongo_port
                        Port of the mongo server
  -v, --verbose         Enables verbosity
  -C, --clean           Cleans logs after usage
```

Some useful tips:

- Setting the `-v` flag will make CORIOLIS generate a more verbose output. This will show more information on errors, like why a rule has not passed.
- The `--timeout` argument controls how many seconds will CORIOLIS wait before forcefully stopping each run of the program under test. Using a value of `0` executes the program on 'interactive mode'.
-  Currently, the languages available are C, C++, Python and Rust. Their values to pass to the `-l` argument are, respectively, `c`, `cpp`, `py` and `rs`.
- CORIOLIS uses MongoDB on the background. If, for some reason, you want to specify a custom MongoDB instance, use the `--mongo_host` and `--mongo_port` arguments.

The CORIOLIS repository already have several examples for every supported language. The following sections explain how to run several of these examples using the previous `coriolis` command.

### Running Python example

A Python implementation of the readers and writers problem can be found on the CORIOLIS repository inside `examples/readersWriters`. Assuming you are on the repository home folder, you can inspect the contents of the `run_coriolis.sh` file to confirm it just runs the code:

```
~$ cat examples/readersWriters/run_coriolis.sh
#!/bin/bash

python3 main.py
```

You can run the example with `coriolis` like the following:

```
~$ coriolis -l py -s examples/readersWriters/ -r coriolis/resources/readers_writers_1_rules.jarl -c coriolis/resources/readers_writers.chk -C
```

### Running Rust example

A Rust implementation of the dinning philosophers problem can be found inside `examples/philosophers` on the CORIOLIS repository. The `run_coriolis.sh` script compiles and runs the code as shown below:

```
~$ cat examples/philosophers/run_coriolis.sh
#!/bin/bash

rustc philos.rs
./philos
```

You can run the example using the next command from the repository home folder:

```
~$ coriolis -l rs -s examples/philosophers/ -r coriolis/resources/philos_1_rules.jarl -c coriolis/resources/philos.chk -C
```

### Running C/C++ example

In order to run C or C++ code with CORIOLIS, you must make sure to link your code against the `coriolis` library. This can be achieved, for instance, by using the `-lcoriolis` flag with `gcc`:

```
~$ gcc -o main main.cpp -lcoriolis
```

For a C++ project with `cmake`, you may only need to add a `target_link_libraries` statement like the following:

```
cmake_minimum_required(VERSION 3.11)

project(myProj)

add_executable(myProj main.cpp)

target_link_libraries(myProj coriolis)
```

You can find a C implementation of the smokers problem in `examples/smokers`. In this case, the `run_coriolis.sh` script uses a `makefile` to compile and run the program:

```
~$ cat examples/smokers/run_coriolis.sh
#!/bin/bash

make
./main
```

To run the example use the following command:

```
~$ coriolis -l c -s examples/smokers/ -r coriolis/resources/smokers_1_rules.jarl -c coriolis/resources/smokers.chk -C
```

## Parsing JARL rules

If you only need to validate a JARL rules file (i.e. check the rules syntax and grammar) you can do so with the `parse` subcommand of CORIOLIS. Executing `coriolis parse -h` will allow you to inspect its usage:

```
~$ coriolis parse -h
usage: coriolis parse [-h] [-r rules_file] [-v]

Parses and validates JARL rules from file.

optional arguments:
  -h, --help            show this help message and exit
  -r rules_file, --rules rules_file
                        Rules .jarl file
  -v, --verbose         Enables verbosity
```

For instance, you can validate the JARL specification examples with the following command from the project's home directory:

```
~$ coriolis parse -r coriolis/resources/jarl_spec_examples.jarl -v
```

## Running user's code

You can run your code and generate CORIOLIS output logs for you to inspect it with the `run` subcommand. You can find more info about this with `coriolis run -h`:

```
~$ coriolis run -h
usage: coriolis run [-h] [-s source] [-d destination] [-l language]
                    [-c checkpoints] [-n number] [-t secs] [-v]

Runs user code producing log files.

optional arguments:
  -h, --help            show this help message and exit
  -s source, --source source
                        Source code directory
  -d destination, --destination destination
                        Logs destination directory
  -l language, --language language
                        Source code language
  -c checkpoints, --checkpoints checkpoints
                        Checkpoint list file
  -n number, --number-runs number
                        Number of runs to perform
  -t secs, --timeout secs
                        Number of seconds to wait before timeout
  -v, --verbose         Enables verbosity
```

You can run an implementation of the sleeping barber problem producing three different output logs on the `output` directory with the following command:

```
~$ coriolis run -l rs -s examples/barber/ -c coriolis/resources/barber.chk -d output/ -n 3
```

## Verifying JARL rules

If you have already generated some CORIOLIS logs with the `run` subcommand, you can inspect them and verify some JARL rules with the `verify` subcommand. The full `coriolis verify -h` command will show all flags for it:

```
~$ coriolis verify -h
usage: coriolis verify [-h] [-l log_path] [-c checkpoints] [-r rules_file]
                       [-H mongo_host] [-p mongo_port] [-v]

Verifies JARL rules based on log files.

optional arguments:
  -h, --help            show this help message and exit
  -l log_path, --log-path log_path
                        Path to check for logs
  -c checkpoints, --checkpoints checkpoints
                        Checkpoint list file
  -r rules_file, --rules rules_file
                        Rules .jarl file
  -H mongo_host, --mongo-host mongo_host
                        Host or IP of the mongo server
  -p mongo_port, --mongo-port mongo_port
                        Port of the mongo server
  -v, --verbose         Enables verbosity
```

CORIOLIS project already includes some previously defined JARL rules for the producer-consumer problem, as well as a sample log file. To verify such rules against the log, just run the next command:

```
~$ coriolis verify -l coriolis/resources/prod_cons_1.log -c coriolis/resources/prod_cons.chk -r coriolis/resources/prod_cons_1_rules.jarl -v
```

