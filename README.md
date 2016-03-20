Yet another log parser
======================

Introduction
------------

This a Python implementation of an Apache2 log parser.

Dependencies
------------

On Ubuntu:

```
apt-get install python-geoip \
  python-ipaddr python-cssselect \
  geoip-database python-jinja2
```

On Mac OS X:
```
brew install geoip
pip install geoip \
  ipaddr lxml cssselect
```

Usage
-----

Clone the Git repository:

```
git clone http://github.com/laurivosandi/yet-another-log-parser
```

Enter the directory and run the program:
```
python main.py
```

To specify output directory:
```
python main.py --output /var/www/html/stats
```

In case your log files are not under /var/log/apache2, specify the directory as following:

```
python main.py --path path/to/log/files/
```

Credits
-------

* Mostly written by Lauri Võsandi, redistribution under MIT license
* [Blank world map from Wikimedia](https://commons.wikimedia.org/wiki/File:BlankMap-World6.svg)