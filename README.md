# ripper
Bulk downloader script

This utility was originally created as a means of downloading a few hundred
items from [Wikisource](https://en.wikisource.org/wiki/Main_Page). Since then,
it's gotten a few overhauls making it progressively uglier, and more to the
point requires direct editing of the source code to adapt to a new target. My
aim here is to make it more general, flexible, and less ugly.

## Status
**Version 0.1.0**

Almost nothing is properly implemented. There is a foundation for the
`GenericRipper` and `Controller` classes which appears mostly in order. So far
they don't do anything, though, so that's next on the agenda.

## General structure

The application consists of one superclass and its three children.

The superclass, `GenericRipper`, exists simply as an abstract class so that the
other three classes will have all their mutual functions.

The root controller class `Controller` is the muscle of the application. It is
the first to be created and the last to die. It manages the web session(s) and
file system access in addition to startup and teardown duty.

Each ripper target lives inside a `Target` class. These handle file naming
policy and dictate directory structure to the `Controller`.

The actual brains is provided by the `Processor` class. These handle the actual
HTML parsing and searching, able to create additional processors and targets as
required by the configuration file.

---
## License
This project is licensed under the
[GNU GPLv3](https://github.com/DrSLDR/ripper/blob/master/LICENSE).
