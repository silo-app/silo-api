from abc import ABC, abstractmethod


class BaseAuthenticator(ABC):

    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass

    @abstractmethod
    def get_fullname(self) -> str:
        """

        Must return the users full name from child class

        Returns:
            str: The users full name. Example: Max Mustermann
        """
        pass
