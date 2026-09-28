# SmokePing

Runs the [linuxserver/smokeping](https://docs.linuxserver.io/images/docker-smokeping/)
image. [SmokePing](https://www.smokeping.org/) measures latency, latency
distribution and packet loss to the hosts you list, and graphs them over time.

## Usage

Open the web UI with **Open Web UI**, or go to
`http://<home-assistant-ip>:7464/smokeping/smokeping.cgi`. The first graphs
appear about 10 minutes after the first start.

## Configuration

On first start the image creates its configuration files in this add-on's
configuration folder, `/addon_configs/<id>_smokeping/` (mounted at `/config`):

| File | Contents |
|---|---|
| `Targets` | The hosts to measure, grouped into menus. **Edit this one first.** |
| `Probes` | How to measure (ping, DNS, HTTP, ...). |
| `Alerts` | Alert patterns and recipients. |
| `Database` | Measurement step and how long results are kept. |
| `General`, `Presentation`, `Slaves`, `pathnames` | General settings, graph layout, remote probes. |

The default `Targets` file contains examples that may not all work. Replace
them with your own hosts, following the format in the file and the
[SmokePing documentation](https://oss.oetiker.ch/smokeping/doc/smokeping_config.en.html),
then restart the add-on to apply the change.

## Data

The measurement databases (RRD files) are in the add-on's `/data` folder,
which is included in Home Assistant backups.

## Ports

The web UI listens on port `80` in the container, published on host port
`7464`. You can change the host port under the add-on's **Network** settings.

## Versions

The add-on version is the image tag. See the
[image releases](https://github.com/linuxserver/docker-smokeping/releases).
