# Helth Check

Health Check is a simple tool that runs a series of tests to check the health
of your system. It returns a system health score and a list of failed tests.
It is designed to run with a daemon that can be used in a lot of different
ways. For example, it can be used in the prompt of your shell to show the
health of your system. It can also be used (with a wrapper) to send
notifications to your email when your system is not healthy (useful for
servers).

## Installation

For now, you can only use the daemon from the source code.

## Usage

### Daemon

The daemon is a D-Bus service that runs the tests and provides a D-Bus
interface to get the health score and the list of failed tests (coming soon).

To run the daemon, you need to have D-Bus installed and running. Then, you can
run the daemon with:

```shell
python3 -m health_check.daemon # Not supported yet, will work when installed
```

You can also run the daemon without installing it:

```shell
python3 .
```

### Client

Since the daemon is a D-Bus service, you can use any D-Bus client to get the
health score and the list of failed tests.

### Shell

In shell, you can use the `dbus-send` command to access the daemon. For
example, to get the health score, you can run:

```shell
dbus-send --session --print-reply --dest=org.healthcheck /org/healthcheck org.healthcheck.Score.get_score`
```

To get only the health score, you can run:

```shell
echo $(dbus-send --session --print-reply --dest=org.healthcheck /org/healthcheck org.healthcheck.Score.get_score 2>/dev/null || echo '-1') | tail -n 1 | awk '{print $NF}'
```

To integrate this in your PowerLevel10k prompt, you can add the following
segment to your `~/.p10k.zsh`:

```zsh
# Health Check
function prompt_healthcheck() {
    local health_score="$(echo $(dbus-send --session --print-reply --dest=org.healthcheck /org/healthcheck org.healthcheck.Score.get_score 2>/dev/null || echo '-1') | tail -n 1 | awk '{print $NF}')"
    # If health score is -1, then healthcheck is not running, so don't show anything
    if (( health_score == -1 )); then
        return
    fi
    # The health score is a number between 0 and 100 (100 being the best), so
    # we can use it to determine the color of the segment
    # In normal use, the score is between 60 and 80, so we'll use that as the
    # threshold for the colors
    if (( health_score >= 80 )); then
        p10k segment -s HEALTHY -f green -i '🏥' -t "${health_score}"
    elif (( health_score >= 60 )); then
        p10k segment -s OK -f 248 -i '🏥' -t "${health_score}"
    elif (( health_score >= 40 )); then
        p10k segment -s WARNING -f yellow -i '🏥' -t "${health_score}"
    elif (( health_score >= 20 )); then
        p10k segment -s DANGER -f red -i '🏥' -t "${health_score}"
    else
        p10k segment -s CRITICAL -f red -i '🏥' -t "${health_score}"
    fi
}
```

and then add `prompt_healthcheck` to your `POWERLEVEL9K_LEFT_PROMPT_ELEMENTS`
or `POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS`.

### Python

You can also access the daemon from Python. The `client.py` file contains an
example of how to do it. Of course, you can also use your own D-Bus client.

## Tests

The tests are located in the `health_check/tests` directory. They are
designed to be as simple as possible. They are also designed to be as
independent as possible. For example, the `battery` test does not depend on
the `cpu` test. This way, you can run the tests on any system, even if some
tests are not supported.

## Contributing

Contributions are welcome. You can contribute by adding new tests or by
improving the existing ones. You can also contribute by improving the daemon
or the client.

The source code is available on [GitHub](https://github.com/Yaya-Cout/HealthCheck).

## License

This project is licensed under the MIT License - see the [COPYING](COPYING)
file for details.
