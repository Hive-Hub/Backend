from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    """
    Abstract Base Class for executing agent logic.
    """

    def __init__(self, agent):
        self.agent = agent

    @abstractmethod
    def execute(self, task, input_data, context=None):
        """
        Perform execution of the given task using the agent configurations and input data.
        Returns a dict:
        {
            "output": str,
            "status": str ('SUCCESS' or 'FAILED'),
            "tokens_used": int,
            "error_message": str (optional)
        }
        """
        pass
