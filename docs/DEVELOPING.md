WIP

## Eventgen Bundles

Eventgen configuration can be packaged in to *Eventgen Bundles*.

### Structure of a bundle

Structurally, bundles are similar to regular Splunk apps. This includes the convention that contents from `local` override the settings from default.

```
. (bundle-dir)
+-- default
|   +-- eventgen.conf                   # Default configuration of the bundle
+-- local
|   +-- eventgen.conf                   # Local overrides (eg. for modifying the outputMode)
+-- lib
|   +-- plugins                         # Directory to store Eventgen plugins (http://splunk.github.io/eventgen/PLUGINS.html)
|       +-- generator
+-- samples                             # Directory for sample files and log templates
    +-- log.template
    +-- items.sample
    +-- templates                       # Sub-directory for jinja templates
        +-- template.j2
```

### Configuring Bundles


#### Output Configuration

Create a local eventgen configuration for the bundle at `bundles/<bundlename>/local/eventgen.conf` in Splunk fashion.
This allows you to selectively override bundle parameters as well as setting the appropriate configuration for your scenario.

```
mkdir bundles/<bundlename>/local
touch bundles/<bundlename>/eventgen.conf
```

In this configuration file, the output mode for the bundle needs to be configured. By default, events are **not** sent to local Splunk, but printed to stdout. Eventgen supports different output formats. Review [eventgen.conf.spec](http://splunk.github.io/eventgen/REFERENCE.html) to learn what is available and identify what is needed for your demo scenario. Note that depending which output format is configured, the command to run the bundle differs.

**HEC Output**

Send data straight to Splunk via [HTTP Event collector (HEC)](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector). Make sure that HEC is enabled and specify the following lines in `local/eventgen.conf`.

```
[global]
outputMode = httpevent
httpeventServers = {"servers":[{ "protocol":"http", "address":"<splunk-host>", "port":"8088", "key":"<hec-token>"}]}
```

Now, to generate events, run the container with the following configuration, replacing `bundle-dir` with the absolute path to the bundle to be generated.

**File Output**

```
[global]
outputMode = file
fileName = /out/access_combined.log
```

### Running bundles

#### Native

Running the sample bundle, outside of docker
```
BUNDLE_DIR=./bundles/hello-eventgen/ splunk_eventgen generate ./bundles/s4r_1/
```


#### Docker

To start generation, run the container while mapping the bundle to the `/bundle` location inside of the container
```
docker run -v $(pwd)/bundles/hello-eventgen/:/bundle eventgen-s4r
```

Since the bundles are baked into the image at build time, it is also possible to run the container without mounting the bundle. Note that this way, changing the configuration of bundles inside the image requires a rebuild.

```
docker run -e BUNDLE_DIR=/s4r/bundles/s4r_1/ eventgen-s4r generate bundles/s4r_1/
```


#### Docker-Compose

The provided docker-compose.yml file will set up a universal forwarder in addition to the Eventgen container. Note that currently, the eventgen does not wait until the UF is ready to read events so some events might be lost in the startup phase.

```
BUNDLE_DIR=./bundles/hello-eventgen docker-compose up
```

**HEC Output**

```
docker run --net=host -v <bundle-dir>:/bundle eventgen-s4r
```

Depending on the deployment model, `--net=host` may or may not be required. For HEC, make sure Eventgen running inside of the container is able to access the HEC endpoint.

**File Output**



### Creating a new bundle

Please review the [Eventgen](http://splunk.github.io/eventgen/) documentation and samples provided in the eventgen [Github repository](https://github.com/splunk/eventgen) to learn how bundles are created.
