import re
import subprocess
import argparse

import requests
from prettytable import PrettyTable


def extract_ip_addresses(destination: str) -> list:
    traceroute = subprocess.Popen(
        ["tracert", "-d", destination], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    ip_addresses = []
    for line in iter(traceroute.stdout.readline, b""):
        line = line.decode("utf-8")
        match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
        if match:
            ip_addresses.append(match.group())
    return ip_addresses


def is_grey_ip(ip: str) -> bool:
    octets = ip.split(".")
    if octets[0] == "192" and octets[1] == "168":
        return True
    elif octets[0] == "10":
        return True
    elif octets[0] == "172" and 15 < int(octets[1]) < 32:
        return True
    else:
        return False


def get_asns(ip_addresses: str) -> dict:
    asns_dict = {}
    for ip_address in ip_addresses:
        response = requests.get(
            f"https://rest.db.ripe.net/search.json?query-string={ip_address}&flags=no-referenced&source=RIPE"
        )
        as_match = re.search(r"AS\d+", response.text)
        country_match = re.search(
            r"\"name\" : \"country\",\s*\"value\" : \"(.*?)\"", response.text, re.S
        )
        asn_description_match = re.search(
            r"\"name\" : \"mnt-by\",\s*\"value\" : \"(.*?)\"", response.text, re.S
        )
        if is_grey_ip(ip_address):
            asns_dict[ip_address] = ["", "", ""]
        else:
            asns_dict[ip_address] = [
                as_match.group() if as_match else "",
                country_match.group(1) if country_match else "",
                asn_description_match.group(1) if asn_description_match else "",
            ]
    return asns_dict


def build_results_table(asns: dict) -> PrettyTable:
    table = PrettyTable()
    table.field_names = ["№", "IP-address", "ASN", "Country", "Provider"]
    for index, (ip, (asn, country, provider)) in enumerate(asns.items()):
        table.add_row([index, ip, asn, country, provider])
    return table


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace IP addresses and display ASN information.")
    parser.add_argument("destination", type=str, help="Domain name or IP address to trace")
    args = parser.parse_args()

    ip_addresses = extract_ip_addresses(args.destination)
    asns = get_asns(ip_addresses)
    table = build_results_table(asns)
    print(table)
