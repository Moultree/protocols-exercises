from dataclasses import dataclass
from typing import List
import dataclasses
import struct


@dataclass
class DNSHeader:
    id: int
    flags: int
    QDCOUNT: int = 0
    ANCOUNT: int = 0
    NSCOUNT: int = 0
    ARCOUNT: int = 0


@dataclass
class DNSQuestion:
    name: bytes
    type_: int
    class_: int


@dataclass
class DNSRecord:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes


@dataclass
class DNSPacket:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSRecord]
    authorities: List[DNSRecord]
    additionals: List[DNSRecord]


def header_to_bytes(header: DNSHeader) -> bytes:
    fields = dataclasses.astuple(header)
    return struct.pack("!HHHHHH", *fields)


def question_to_bytes(question: DNSQuestion) -> bytes:
    return question.name + struct.pack("!HH", question.type_, question.class_)


def ip_to_string(ip: bytes) -> str:
    return ".".join([str(x) for x in ip])
