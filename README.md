# s4r-eventgen

Standalone, containerized [Eventgen](http://splunk.github.io/eventgen/) originally developed for Splunk 4 Rookies (S4R).

## Getting Started
The following section will help you set up and run s4r-eventgen.

### Prerequisites

* Docker (See [Installation Instructions](https://docs.docker.com/get-docker/))

### Installation
First, the Docker container image needs to be created from the source in this repo.

1. Clone this repository
```
git clone https://github.com/mark-sivill-splunk/splunk4rookies-eventgen
```

2. Change into the directory and build the container image
```
cd splunk4rookies-eventgen
docker build -t s4r-eventgen .
```

After the build terminates, you should have a docker image named **s4r-eventgen**, ready to run.

### Quick Start

To run the **hello-world** bundle which is part of the container image. Execute the following command. Please make sure the trailing slash is present.

```
docker run s4r-eventgen /repo/bundles/hello-world/
```

If you see some JSON data on your console after a short delay - great! If not, please review the [Troubleshooting](#troubleshooting) section of this README.

### Usage Examples

#### Running a pre-built bundle with file output

The bundle **s4r_access_combined** outputs events to multiple files which can be picked up by a universal forwarder (UF). 

To write the data into a directory on the Docker host, we map `$(pwd)/out` (a subfolder called `out` in the current working directory) to `/out` which is where the bundle will write the events (as configured in `bundles/s4r_access_combined/default/eventgen.conf`).

```
docker run -v $(pwd)/out:/out s4r-eventgen /repo/bundles/s4r_access_combined/
```

#### Running a user-provided bundle with file output

We can also use the s4r-eventgen image to run bundles which have been not baked into the image at build-time. To do this, the bundle directory from the host is mounted into the `/bundle` location inside of the container.
```
docker run -v $(pwd)/out:/out -v $(pwd)/bundles/s4r_access_combined/:/bundle s4r-eventgen
```


### Troubleshooting

Most issues are likely to be related to the provided paths. Make sure that trailing slashes are placed, where needed and check all paths and directories used in bind mounts exist on the host.

#### Debug Logging
You can set the log verbosity of Eventgen by supplying the `-e DEBUG=1` to the command. To read the logs, bind `/logs` inside the container to an existing directory on the host. In this case, it is mounted to the `/tmp/` directory.

```
docker run -e DEBUG=1 -v $(pwd)/tmp/:/logs s4r-eventgen /repo/bundles/hello-world/
```

#### Removing a running docker 

When running the Docker container without the `-d` flag, container execution, it can be terminated by pressing CTRL-C, sending SIGTERM to the container. When running in detached mode, `docker stop` or `docker kill` can be used to terminate a container after identifying it through `docker ps`.


## Contributors

* Mark Sivill
* Daniel Federschmidt


### Reference

#### Container Directories

The following directories inside the container are useful to bind to the host.
```
/
+-- logs                                # Directory where Eventgen writes it's logs
+-- out                                 # Directory that bundles with file outputMode should place their files in
+-- bundle                              # Directory where a user-provided bundle should be mounted 
```
