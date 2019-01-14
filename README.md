# Python Wrapper for ExifTool

## Prerequisites

Have [Python 3](https://www.python.org/) and [ExifTool](http://owl.phy.queensu.ca/~phil/exiftool/) installed.

## Summary

Simply run ```python exiftool_backend_test.py``` to run a series of unit tests that read and write custom EXIF tags using ExifTool. Running the tests outputs the command you would execute on a *NIX shell.

The testing code in `exiftool_backend_test.py` and `backend_test.py` is not very interesting and is a bit over-engineered since it was adapted from a different projet.

`exiftool_backend.py` is where ExifTool commands are created, executed and their output parsed.

`custom.config` is an ExifTool configuration file where we can specify any custom tags (not already supported by the file format), we want to insert in the file.

## References

[ExifTool Command-Line Examples](http://owl.phy.queensu.ca/~phil/exiftool/examples.html)
[ExifTool FAQ](https://sno.phy.queensu.ca/~phil/exiftool/faq.html): In particular, question 11 on user-defined tags.
