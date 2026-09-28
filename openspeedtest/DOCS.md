# OpenSpeedTest

Runs the official, unmodified
[openspeedtest/latest](https://hub.docker.com/r/openspeedtest/latest) image: a
browser-based speed test between any device on your network and the machine
running Home Assistant. It is an alternative to running `iperf3` on both ends.

## Usage

Start the add-on, then open `http://<home-assistant-ip>:3000` in a browser on
the device you want to test (or use **Open Web UI**). The test measures
download, upload, ping and jitter between that browser and the Home Assistant
host.

There is nothing to configure.

## Ports

| Container port | Default host port | Use |
|---|---|---|
| `3000/tcp` | `3000` | HTTP |
| `3001/tcp` | disabled | HTTPS |

To use HTTPS, set a host port for `3001/tcp` under the add-on's **Network**
settings.

## Versions

The add-on version is the image tag. See the
[image releases](https://github.com/openspeedtest/Docker-Image/releases).
