# pynes

[![Build Status](https://travis-ci.com/ipwnponies/pynes.svg?branch=master)](https://travis-ci.com/ipwnponies/pynes)
[![Coverage Status](https://img.shields.io/coveralls/github/ipwnponies/pynes.svg)](https://coveralls.io/github/ipwnponies/pynes?branch=master)
![license](https://img.shields.io/github/license/ipwnponies/pynes.svg)

Yet another pet project to write a Nintendo Entertainment System (NES) emulator.
This is for my own learning and understanding.
What I'd like to do differently is to better document the process that my predecessors, from a python developer's
perspective.
The documentation is scattered, but abundant, and most existing toy implementations were written as personal projects
(no comment or doc strings, magic variables, tests are non-existent, etc.).

At the very least, you might be able to write your own emulator and test it against these existing tests, instead of
testing against validation NES roms.

## Dependencies

This project is written for python 3.7.

## Installation

Simply install this in the same python environment that `pytest` uses and the rest is magic.

```sh
make venv
```

## How to test the software

```sh
make test
```

----

## Credits and references
