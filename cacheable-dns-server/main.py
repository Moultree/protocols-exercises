from io import BytesIO
import socket
import random
import argparse
import struct
from utils import (
    DNSHeader,
    DNSQuestion,
    DNSRecord,
    DNSPacket,
    header_to_bytes,
    ip_to_string,
    question_to_bytes,
)
from cache_helper import CacheHelper as Cache

TYPE_A = 1
TYPE_NS = 2
CLASS_IN = 1

ROOT_SERVER = "198.41.0.4"


class DNSServer:
    def __init__(self):
        self.cache = Cache()

    def get_answer(self, packet: DNSPacket) -> str:
        if packet is None:
            return None

        for answer in packet.answers:
            if answer.type_ == TYPE_A:
                return answer.data

    def get_nameserver(self, packet: DNSPacket) -> str:
        if packet is None:
            return None

        for authority in packet.authorities:
            if authority.type_ == TYPE_NS:
                return authority.data.decode("utf-8")

    def encode_dns_name(self, domain_name: str) -> bytes:
        encoded = b""
        for part in domain_name.encode("ascii").split(b"."):
            encoded += bytes([len(part)]) + part

        return encoded + b"\x00"

    def decode_name(self, reader: BytesIO) -> bytes:
        parts = []
        while (length := reader.read(1)[0]) != 0:
            if length & 0b11000000:
                parts.append(self.decode_compressed_name(length, reader))
                break
            else:
                parts.append(reader.read(length))

        return b".".join(parts)

    def decode_compressed_name(self, length: int, reader: BytesIO) -> bytes:
        pointer_bytes = bytes([length & 0b00111111]) + reader.read(1)
        pointer = struct.unpack("!H", pointer_bytes)[0]
        current_pos = reader.tell()
        reader.seek(pointer)
        result = self.decode_name(reader)
        reader.seek(current_pos)

        return result

    def parse_header(self, reader: BytesIO) -> DNSHeader:
        items = struct.unpack("!HHHHHH", reader.read(12))

        return DNSHeader(*items)

    def parse_question(self, reader: BytesIO) -> DNSQuestion:
        name = self.decode_name(reader)
        data = reader.read(4)
        type_, class_ = struct.unpack("!HH", data)

        return DNSQuestion(name, type_, class_)

    def parse_record(self, reader: BytesIO) -> DNSRecord:
        name = self.decode_name(reader)
        data = reader.read(10)
        type_, class_, ttl, data_len = struct.unpack("!HHIH", data)

        if type_ == TYPE_A:
            data = ip_to_string(reader.read(data_len))
        elif type_ == TYPE_NS:
            data = self.decode_name(reader)
        else:
            data = reader.read(data_len)

        return DNSRecord(name, type_, class_, ttl, data)

    def parse_dns_packet(self, data: bytes) -> DNSPacket:
        reader = BytesIO(data)
        header = self.parse_header(reader)

        questions = [
            self.parse_question(reader) for _ in range(header.QDCOUNT)
        ]
        answers = [
            self.parse_record(reader) for _ in range(header.ANCOUNT)
        ]
        authorities = [
            self.parse_record(reader) for _ in range(header.NSCOUNT)
        ]
        additionals = [
            self.parse_record(reader) for _ in range(header.ARCOUNT)
        ]

        return DNSPacket(header, questions, answers, authorities, additionals)

    def build_query(self, domain_name: str, record_type: int) -> bytes:
        random.seed(1)

        name = self.encode_dns_name(domain_name)
        id = random.randint(0, 65535)
        header = DNSHeader(id=id, flags=0, QDCOUNT=1)
        question = DNSQuestion(name=name, type_=record_type, class_=CLASS_IN)

        return header_to_bytes(header) + question_to_bytes(question)

    def send_query(
        self, ip_address: str, domain_name: str, record_type: int
    ) -> DNSPacket:
        query = self.build_query(domain_name, record_type)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)

        try:
            sock.sendto(query, (ip_address, 53))
            data, _ = sock.recvfrom(1024)
        except socket.timeout:
            print("DNS query timed out")
            return None
        except socket.error as e:
            print(f"An error occurred while sending the query: {e}")
            return None
        finally:
            sock.close()

        return self.parse_dns_packet(data)

    def resolve(self, domain_name: str, record_type: int) -> str | None:
        additional = {}

        try:
            server_name = ROOT_SERVER
            if cached_data := self.cache.get(domain_name):
                return (
                    f"IP found in cache: {cached_data[0]}\n"
                    f"Additional: {cached_data[1]}"
                )
            while True:
                print(f"Querying {server_name} for {domain_name}")
                response = self.send_query(
                    server_name, domain_name, record_type
                )
                if response:
                    for record in response.additionals:
                        if record.type_ == TYPE_A:
                            additional[record.name.decode()] = record.data
                if ip := self.get_answer(response):
                    self.cache.set(
                        domain_name, ip, additional, response.answers[0].ttl
                    )
                    return ip
                elif ns_ip := self.get_nameserver(response):
                    server_name = ns_ip
                elif ns_domain := self.get_nameserver(response):
                    server_name = self.resolve(ns_domain, TYPE_A)
                else:
                    return "Something went wrong..."
        except KeyboardInterrupt:
            self.cache.dump("cache")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Server")
    parser.add_argument("domain", type=str, help="Domain name to resolve")
    args = parser.parse_args()

    DNSServer = DNSServer()
    DNSServer.cache.load("cache")
    result = DNSServer.resolve(args.domain, TYPE_A)
    print(result)
    DNSServer.cache.dump("cache")