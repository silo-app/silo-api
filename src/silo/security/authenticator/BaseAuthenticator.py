from abc import ABC, abstractmethod


class BaseAuthenticator(ABC):

    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass
