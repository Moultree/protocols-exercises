# TCP-UDP Port scanner

Author: Tikhonchik Nikolay (`okaykudes@gmail.com`)  

## About

This is a Python program that scans TCP and UDP ports on a given host. It uses multithreading to scan multiple ports simultaneously.

## Usage

To run the script, you need to do the following:  

```bash
python scanner.py host min_port max_port
```

- Replace host with the target host IP or domain name, min_port with the minimum port number to scan, and max_port with the maximum port number to scan.

## Sample Usage

```bash
python scanner.py youtube.com 1 500
TCP 80 is open
TCP 443 is open
```
