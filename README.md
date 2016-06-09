# bandwidth-monitor
#### Description
Scrape bandwidth statistics from router's web interface every `n` seconds.

Written for the [TP Link TD-W8960N] Modem Router.

#### Requirements
- Python 2.7
- [Requests] library

#### Usage
```
$ python bandwidth-monitor.py -h

Description: Displays the amount of bandwidth passing through the router

Usage: bandwidth-monitor [passwordHash] [interval]

passwordHash : MD5 Hash of the admin password
interval     : Seconds between polling the router for stats
```

Directly provide password MD5 hash:
```
$ python bandwidth-monitor.py c476eda4bd8ba5eb5d2db57d523c3e45
```

Example Output:
```
Total Down (MiB): 26 (435 KiB/s)
Total Up (MiB): 4 (11 KiB/s)
```

[Requests]:http://docs.python-requests.org/en/master/
[TP Link TD-W8960N]:http://www.tp-link.co.za/products/details/cat-15_TD-W8960N.html
