# Note as implemented this plugin is not threadsafe, file should only be used with one output worker
import os
import random
import logging

from splunk_eventgen.lib.logging_config import logger
from splunk_eventgen.lib.outputplugin import OutputPlugin


class MultiFileOutputPlugin(OutputPlugin):
    name = "file"
    MAXQUEUELENGTH = 10
    useOutputQueue = False

    validSettings = ["fileMaxBytes", "fileBackupFiles", "fileFiles"]
    intSettings = ["fileMaxBytes", "fileBackupFiles", "fileFiles"]

    def __init__(self, sample, output_counter=None):
        OutputPlugin.__init__(self, sample, output_counter)

        if sample.fileName is None:
            logger.error(
                "outputMode file but file not specified for sample %s"
                % self._sample.name
            )
            raise ValueError(
                "outputMode file but file not specified for sample %s"
                % self._sample.name
            )

        self._file = sample.pathParser(sample.fileName)
        self._fileMaxBytes = sample.fileMaxBytes
        self._fileBackupFiles = sample.fileBackupFiles
        self._fileFiles = sample.fileFiles
        
        def new_name(name, i):
            split = name.rsplit(".", 1)
            if len(split) == 1:
                return "{}_{}".format(name, i)
            else:
                return "{}_{}.{}".format(split[0], i, split[1])

        self._multifiles = [new_name(self._file, i) for i in range(int(self._fileFiles))]
        self._fileHandles = [open(file, "a") for file in self._multifiles]
        self._fileLengths = [os.stat(file).st_size for file in self._multifiles]

    def flush(self, q):
        if len(q) > 0:
            logger.debug(
                "Flushing output for sample '%s' in app '%s' for queue '%s'"
                % (self._sample.name, self._app, self._sample.source)
            )
            # Select random file
            rnd = random.randint(0, int(self._fileFiles) - 1)

            self._fileHandle = self._fileHandles[rnd]
            self._fileLength = self._fileLengths[rnd]
            self._file = self._multifiles[rnd]

            # Loop through all the messages and build the long string, write once for each flush
            # This may cause the file exceed the maxFileBytes a little bit but will greatly improve the performance
            try:
                for metamsg in q:
                    msg = metamsg.get("_raw")
                    if not msg:
                        continue
                    if msg[-1] != "\n":
                        msg += "\n"

                    if self._fileLength + len(msg) <= self._fileMaxBytes:
                        self._fileHandle.write(msg)
                        self._fileLength += len(msg)
                    else:
                        self._fileHandle.flush()
                        self._fileHandle.close()
                        
                        if os.path.exists(
                            self._file + "." + str(self._fileBackupFiles)
                        ):
                            logger.debug(
                                "File Output: Removing file: %s" % self._file
                                + "."
                                + str(self._fileBackupFiles)
                            )
                            try:
                                os.unlink(self._file + "." + str(self._fileBackupFiles))
                            except FileNotFoundError:
                                continue

                        for x in range(1, int(self._fileBackupFiles))[::-1]:
                            logger.debug(
                                "File Output: Checking for file: %s" % self._file
                                + "."
                                + str(x)
                            )
                            try:
                                if os.path.exists(self._file + "." + str(x)):
                                    logger.debug(
                                        "File Output: Renaming file %s to %s"
                                        % (
                                            self._file + "." + str(x),
                                            self._file + "." + str(x + 1),
                                        )
                                    )
                                    os.rename(
                                        self._file + "." + str(x),
                                        self._file + "." + str(x + 1),
                                    )
                            except FileNotFoundError:
                                logger.debug("Could not move file, we'll try next time")
                                continue
                        os.rename(self._file, self._file + ".1")
                        self._fileHandle = open(self._file, "a")
                        self._fileHandles[rnd] = self._fileHandle
                        self._fileHandle.write(msg)
            except IndexError:
                logger.debug(
                    "IndexError when writting for app '%s' sample '%s'"
                    % (self._app, self._sample.name)
                )

            if not self._fileHandle.closed:
                self._fileHandle.flush()
            logger.debug(
                "Queue for app '%s' sample '%s' written"
                % (self._app, self._sample.name)
            )

            self._fileHandle.close()


def load():
    """Returns an instance of the plugin"""
    return MultiFileOutputPlugin
