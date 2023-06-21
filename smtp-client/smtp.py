import base64
import json
import mimetypes
import socket
import ssl
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

boundary = "bound.73899"


@dataclass
class Config:
    secret: str

    subject: str
    send_to: str | list
    send_from: str
    attachment: str = None


@dataclass
class Message:
    file_path: str

    subject: str
    send_to: list
    send_from: str
    attachment: Path = None

    date: datetime = None

    def generate_attachment(self, file: Path):
        with file.open("rb") as f:
            return [
                f"--{boundary}",
                "Content-Disposition: attachment;",
                f'  filename="{file.name}"',
                "Content-Transfer-Encoding: base64",
                f"Content-Type: {mimetypes.guess_type(file)[0]};",
                f'        name="{file.name}"',
                "",
                base64.b64encode(f.read()).decode(),
            ]

    def _build(self):
        self.date = self.date or datetime.now()
        content_type = "multipart/mixed"

        headers = [
            f'Date: {self.date.strftime("%d/%m/%y")}',
            f"From: {self.send_from}",
            f"To: {', '.join(self.send_to)}",
            f"Subject: {self.subject}",
            "MIME-Version: 1.0",
            f"Content-Type: {content_type};",
            f"  boundary={boundary}",
            "",
        ]

        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        body = [
            f"--{boundary}",
            "Content-Type: text/html",
            "",
            f"{content}",
        ]
        if self.attachment:
            if self.attachment.is_dir():
                for file in self.attachment.glob("*"):
                    body.extend(self.generate_attachment(file))
            elif self.attachment.is_file():
                body.extend(self.generate_attachment(self.attachment))

        body.append(f"--{boundary}--")

        return "\n".join(headers) + "\n" + "\n".join(body) + "\n.\n"

    def __str__(self) -> str:
        return self._build()


class SMTPClient:
    SMTP_HOST = "smtp.yandex.ru"
    SMTP_PORT = 465

    def __init__(
        self,
        config_path: str = "config.json",
    ) -> None:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
            self.config = Config(**config)

    def request(self, client: ssl.SSLSocket, message_request: str) -> bytes:
        client.send((message_request + "\n").encode("utf-8"))

        recv_data = client.recv(65536)
        return recv_data

    def _get_context(self) -> ssl.SSLContext:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        return context

    def send(self, file_path: str):
        login = base64.b64encode(
            self.config.send_from.encode("utf-8")
        ).decode()
        secret = base64.b64encode(self.config.secret.encode("utf-8")).decode()

        sequence = [
            f"EHLO {self.config.send_from}",
            "AUTH LOGIN",
            login,
            secret,
            f"MAIL FROM:{self.config.send_from}",
            "DATA",
            str(
                Message(
                    file_path,
                    subject=self.config.subject,
                    send_to=self.config.send_to,
                    send_from=self.config.send_from,
                    attachment=Path(self.config.attachment)
                    if self.config.attachment
                    else None,
                )
            ),
        ]

        for reciever in self.config.send_to:
            sequence.insert(
                5,
                f"RCPT TO:{reciever}",
            )

        with socket.create_connection(
            (self.SMTP_HOST, self.SMTP_PORT)
        ) as sock:
            try:
                with self._get_context().wrap_socket(
                    sock, server_hostname=self.SMTP_HOST
                ) as client:
                    client.recv(1024)
                    for request in sequence:
                        print(self.request(client, request))
            except socket.error as error:
                print("Socket error occurred:", error)


if __name__ == '__main__':
    cl = SMTPClient()
    cl.send("message.txt")
