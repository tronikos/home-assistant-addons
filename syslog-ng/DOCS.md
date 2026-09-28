# syslog-ng

Runs the [linuxserver/syslog-ng](https://docs.linuxserver.io/images/docker-syslog-ng/)
image: a syslog receiver for routers, access points and other devices on your
network, storing their logs in Home Assistant's `share` folder.

## Sending logs to it

Point your devices' remote syslog at the Home Assistant host:

| Port | Protocol |
|---|---|
| `5514` | UDP |
| `6601` | TCP |

Many devices can only send to the standard UDP port `514`. In that case, change
the host port for `5514/udp` to `514` under the add-on's **Network** settings.

## Where logs go

The `share` folder is mounted at `/var/log` in the container, so a file written
to `/var/log/<name>` appears as `/share/<name>` in Home Assistant.

With the image's default configuration, every received message is appended to:

- `/share/messages`
- `/share/messages-kv.log` (the same messages with all name-value pairs)

**Neither file is rotated, so both grow without limit.** The image has no
`logrotate`. For a bounded set of files, see the example below.

## Configuration

On first start the image creates `syslog-ng.conf` in this add-on's configuration
folder, `/addon_configs/<id>_syslog-ng/` (mounted at `/config`). Edit it and
restart the add-on to apply the change. See the
[syslog-ng documentation](https://syslog-ng.github.io/) for the syntax.

The add-on runs syslog-ng as root, so files it creates are owned by root.

### Example: one file per day of the month

syslog-ng's `file()` destination can't rotate, but it can overwrite a file whose
name repeats. With the day of the month in the file name,
`overwrite-if-older()` keeps about one month of logs:

```
destination d_local {
  file("/var/log/syslog/messages-${R_DAY}"
    create-dirs(yes)
    overwrite-if-older(172800)
    perm(0644) dir-perm(0755)
    flush-lines(1)
  );
};
```

- `overwrite-if-older(172800)` starts the file over when it was last written
  more than two days ago, i.e. when the same day of the next month comes round.
- `perm(0644) dir-perm(0755)` make the files readable by non-root users, such as
  the Terminal & SSH add-on.
- `flush-lines(1)` writes each line immediately. With a low message rate, larger
  values can hold lines in memory for hours.

Use this `d_local` in place of the default one, and filter what reaches it in the
`log {}` block to keep the files small.

## Checking that messages arrive

```
docker exec app_<id>_syslog-ng syslog-ng-ctl stats --control=/config/syslog-ng.ctl
```

from the Home Assistant host shows the received and written message counters.

## Versions

The add-on version is the image tag. See the
[syslog-ng releases](https://github.com/syslog-ng/syslog-ng/releases).
