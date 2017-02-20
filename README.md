# mathdraw

[![Build Status](https://travis-ci.org/mtib/mathdraw.svg?branch=master)](https://travis-ci.org/mtib/mathdraw)

This is a virtual whiteboard application ment for mathmatics. It works based on a client
server structure (both included in this repository). Users are anonym to each other, the
number of users can be changed in the server.

The clients see a canvas with theoretically ~((2^64)^2) workspaces. All actions are
replicated on all users canvas.

## usage

```
LMB    =                        Painting
RMB    =                         Erasing
MMB    = Cycle colors (red, green, blue)
Arrows =                Change Workspace
t      =                      Text Input
T      =                       Cli Input
Return =                  End Text Input
```

## contribution

```
#TODO tell everyone to do with it as they like
      but try to follow the roadmap
```

## roadmap

Things that would improve this application:

- cli color selector
- gui color selector
- native plotter (not tex based)
- following mechanic (for changing workspace)
- variable resolution
- variable aspect ratio
- optimize netcode (non ascii)
