from abc import ABC, abstractmethod

from silo.schemas import AuthData, UserAttributes


class BaseAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, **kwargs: AuthData) -> bool:
        pass

    @abstractmethod
    def get_user_attributes(self) -> UserAttributes:
        pass
