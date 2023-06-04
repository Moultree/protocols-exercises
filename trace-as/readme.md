# Trace autonomous systems

Author: Tikhonchik Nikolay (`okaykudes@gmail.com`)  
Link to YouTube video -> [[Link](https://www.youtube.com/watch?v=RtLtLs1Diwg)]

## About

The code is a Python script that allows the user to input a domain name or IP address and performs a traceroute to the destination.  
It then extracts the IP addresses of the intermediate hops and retrieves the Autonomous System Number (ASN), country, and provider information for each IP address using the RIPE database.  
The script filters out "grey IPs" (private IP addresses) and outputs the results in a table using the PrettyTable library. 

## Installation

First, install the requrements:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, you need to do the following:  

```bash
python main.py destination
```