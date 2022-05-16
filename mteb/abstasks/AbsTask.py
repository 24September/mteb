from abc import ABC, abstractmethod
import datasets


class AbsTask(ABC):
    def __init__(self, **kwargs):
        self.dataset = None
        self.data_loaded = False

    def load_data(self):
        """
        Load dataset from HuggingFace hub
        """
        if self.data_loaded:
            return

        self.dataset = datasets.load_dataset(self.description["hf_hub_name"])
        self.data_loaded = True

    @abstractmethod
    def description(self):
        """
        Returns a description of the task. Should contain the following fields:
        name: Name of the task (usually equal to the class name. Should be a valid name for a path on disc)
        description: Longer description & references for the task
        type: Of the set: [sts]
        available_splits: Available splits as list, e.g. ['dev', 'test']
        main_score: Main score value for task
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, model, split="test"):
        """
        Evaluates a Sentence Embedding Model on the task.
        Returns a dict (that can be serialized to json).
        :param model: Sentence embedding method. Implements a encode(sentences) method, that encodes sentences
        and returns a numpy matrix with the sentence embeddings
        :param split: Which datasplit to be used.
        """
        raise NotImplementedError
