# Marvinbot Transcript Plugin

Transcribes telegram voice note to text using Google Speech Recognition.

# Requirements

-   A working [Marvinbot](https://github.com/BotDevGroup/marvin) install

# Getting Started

You need to create the json authentication file and set the env GOOGLE_APPLICATION_CREDENTIALS.

[Getting Started with Authentication](https://cloud.google.com/docs/authentication/getting-started)

# Run

```
$ export GOOGLE_APPLICATION_CREDENTIALS=/home/marvin/cloud_api.json

$ ./marvind start
```


```
$ env GOOGLE_APPLICATION_CREDENTIALS=/home/marvin/cloud_api.json ./run_standalone.py
```