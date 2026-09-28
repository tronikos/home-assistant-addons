# Homebridge

Runs the official, unmodified
[homebridge/homebridge](https://hub.docker.com/r/homebridge/homebridge) image,
which exposes non-HomeKit devices to Apple Home through Homebridge plugins.

## First start

1. Start the add-on and open the web UI (**Open Web UI**, port `8581`).
2. Create the administrator account the UI asks for on first use.
3. Install plugins and pair the bridge with Apple Home from the UI, as described
   in the [Homebridge documentation](https://github.com/homebridge/homebridge/wiki).

## Network

The add-on uses the host network, because HomeKit discovery (mDNS) and the
bridges' HAP ports need to be reachable directly on your LAN. Port `8581` is
the web UI.

## Data

Everything Homebridge stores, including `config.json`, the installed plugins,
paired accessories and cached state, is in this add-on's configuration folder,
`/addon_configs/<id>_homebridge/` (mounted at `/homebridge` in the container).

`node_modules` is excluded from Home Assistant backups. After a restore, the
image's start script finds it missing and runs `npm install` in that folder,
which reinstalls Homebridge and the plugins listed in `package.json`.

## Versions

The add-on version is the image tag, a date such as `2026-09-25`. See the
[image releases](https://github.com/homebridge/docker-homebridge/releases).
