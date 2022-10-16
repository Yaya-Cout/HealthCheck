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
dbus-send --session --print-reply --dest=org.healthcheck /org/healthcheck org.healthcheck.Score.get_score | tail -n 1 | awk '{print $2}'
```

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
