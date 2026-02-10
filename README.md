# qrm, a Bot for Discord

A discord bot with ham radio functionalities.

qrm3 is a fork of [qrm2](https://github.com/miaowware/qrm2), a project by MiaowWare.

This fork is a Python 3.13+ fork maintained by JayToTheAy.

## Running

### With Docker

See [README-DOCKER.md](./README-DOCKER.md)

### Without Docker

Requires Python 3.13 or newer.

Prep the environment. For more information on extra options, see the [quick-bot-no-pain Makefile documentation](https://github.com/0x5c/quick-bot-no-pain/blob/master/docs/makefile.md).

Install `libcairo` and `libjpeg` (package names may vary by distro or OS). Then run:

```
$ make install
```

Run. For more information on options, see the [quick-bot-no-pain run.sh documentation](https://github.com/0x5c/quick-bot-no-pain/blob/master/docs/run.sh.md).

```
$ run.sh
```

## Contributing

Check out the [development](/DEVELOPING.md) guidelines for more information about developing for this project.

Contributions should abide by MiaowWare's [original contribution guidelines](https://github.com/miaowware/.github/blob/master/CONTRIBUTING.md).

All issues and requests related to resources (including maps, band charts, data) should be added in [miaowware/qrm-resources](https://github.com/miaowware/qrm-resources).

## Copyright

Copyright (C) 2019-2023 classabbyamp, 0x5c
Copyright (C) 2026 jaytotheay

This program is released under the terms of the *Québec Free and Open-Source Licence – Strong Reciprocity (LiLiQ-R+)*, version 1.1.
See [`LICENCE`](LICENCE) for full license text (Français / English).
