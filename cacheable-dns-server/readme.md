# Cacheable DNS Server

Author: Tikhonchik Nikolay (`okaykudes@gmail.com`)  
Link to YouTube video -> [[Link](https://youtu.be/M_1XR0wgRnY)]

## About

This is a cacheable DNS server implementation that listens on port 53. The server resolves recursive queries and caches the obtained information. The cache is used to store the resolved domain names and their corresponding IP addresses, as well as the reverse mapping of IP addresses to domain names.

## Files

`main.py`: Contains the main implementation of the DNS server.\
`utils.py`: Includes utility functions for DNS packet parsing and conversion.\
`cache_helper.py`: Provides a helper class for caching DNS records and managing cache operations.

## Usage

To run the script, you need to do the following:  

```bash
python main.py

Enter domain name: yourdomain.com
```

## Note
The server assumes the root server's IP address is set as `198.41.0.4`. Modify the ROOT_SERVER variable in main.py if necessary.