import time
import pickle


class CacheHelper:
    def __init__(self) -> None:
        self.cache: dict[str, tuple[str, int, dict[str, str]]] = {}

    def set(
        self, key: str, value: str, additional: dict = {}, ttl: int = 0
    ) -> None:
        self.cache[key] = (value, time.time() + ttl, additional)

    def get(self, key: str) -> tuple | None:
        if key in self.cache:
            value, ttl, additional = self.cache[key]
            if ttl == 0 or time.time() < ttl:
                return value, additional
            else:
                del self.cache[key]
        return None

    def dump(self, filename: str) -> None:
        with open(filename, "wb") as f:
            pickle.dump(self.cache, f)

    def load(self, filename: str) -> None:
        try:
            with open(filename, "rb") as f:
                self.cache = pickle.load(f)
        except FileNotFoundError:
            self.cache = {}
