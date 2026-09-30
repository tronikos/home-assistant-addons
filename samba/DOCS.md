# Samba

A Samba file server for the Home Assistant folders, running the
[crazymax/samba](https://github.com/crazy-max/docker-samba) image. Unlike the
official Samba share add-on, it supports several users with different access
per share. Users and shares are defined in a YAML file rather than in the UI.

## Configuration

Create `config.yml` in this add-on's configuration folder, which is
`/addon_configs/<id>_samba/` (the `addon_configs` share, or
`/addon_configs` in the Terminal & SSH add-on), then start or restart the
add-on. The format is described in the
[image's documentation](https://github.com/crazy-max/docker-samba#configuration).

The Home Assistant folders are mounted under `/samba`:

| Folder | Path |
|---|---|
| Home Assistant configuration | `/samba/config` |
| Local add-ons | `/samba/addons` |
| Add-on configurations | `/samba/addon_configs` |
| Share | `/samba/share` |
| Media | `/samba/media` |
| Backups | `/samba/backup` |
| SSL | `/samba/ssl` |

Example with an administrator who can use every share and a second user who
can only use `media`:

```yaml
auth:
  - user: admin
    group: admin
    uid: 1000
    gid: 1000
    password: change-me
  - user: homeassistant
    group: homeassistant
    uid: 1001
    gid: 1001
    password: change-me-too

global:
  # Keep Samba's runtime databases in the container's RAM disk. The image's
  # health check opens an SMB session every 30 seconds, and with the default
  # location each check rewrites these files on the Home Assistant disk.
  - "lock directory = /dev/shm"
  - "cache directory = /dev/shm"
  # Home Assistant's folders are owned by root.
  - "force user = root"
  - "force group = root"

share:
  - name: config
    path: /samba/config
    browsable: yes
    readonly: no
    guestok: no
    validusers: admin
    writelist: admin
  - name: media
    path: /samba/media
    browsable: yes
    readonly: no
    guestok: no
    validusers: admin homeassistant
    writelist: admin homeassistant
```

Add one `share` entry per folder you want to expose.

## Allowed hosts

By default only local networks can connect: `127.0.0.1 10.0.0.0/8
172.16.0.0/12 192.168.0.0/16 169.254.0.0/16 fe80::/10 fc00::/7`. To allow
other addresses, for example a VPN client, add a complete list to `global`:

```yaml
global:
  - "hosts allow = 127.0.0.1 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 169.254.0.0/16 fe80::/10 fc00::/7 100.64.0.1"
```

## Discovery

Windows finds the server through WS-Discovery (WSDD2). NetBIOS is disabled,
so there is no network browsing over NetBIOS and no master browser election.
Other clients can connect with `smb://<home-assistant-ip>/<share>`.

WSDD2 announces the server as `homeassistant` and answers only on `eno0`
(`WSDD2_HOSTNAME` and `WSDD2_INTERFACE` in `config.yaml`). Without an
interface it binds every Docker veth interface and rebinds, with a log entry,
whenever a container starts or stops. Its LLMNR TCP listener always logs
`bind: Address in use` once at startup, because the host's resolver already
holds port 5355 on the host network; name lookups still work through the host.
If your host's LAN interface isn't `eno0` (check with `ip -br link` in the
Terminal add-on), change `WSDD2_INTERFACE`, since environment variables of an
image-only add-on can't be set from its options.

## Image version

The add-on runs the `edge` tag. The `4.23.8` release also starts a `socklog`
service that keeps failing to bind `/dev/log`, which Home Assistant mounts
into every add-on for logging; `edge` no longer has that service. Move to the
next numbered release once it is published.
