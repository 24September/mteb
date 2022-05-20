from .AbsTask import AbsTask
import datasets
from ..evaluation.evaluators import (
    kNNClassificationEvaluator,
    logRegClassificationEvaluator,
    kNNClassificationEvaluatorPytorch,
)
import numpy as np
import logging
from collections import defaultdict


class AbsTaskKNNClassification(AbsTask):
    """
    Abstract class for kNN classification tasks
    The similarity is computed between pairs and the results are ranked. Average precision
    is computed to measure how well the methods can be used for classification. #TODO:
    """

    def __init__(self, **kwargs):
        super(AbsTaskKNNClassification, self).__init__(**kwargs)
        self.method = kwargs.get("method", "kNN")
        self.k = kwargs.get("k", 3)

    def evaluate(self, model, eval_split="test", train_split="train"):
        if not self.data_loaded:
            self.load_data()

        if self.is_multilingual:
            scores = {}
            for lang in self.langs:
                print(f"\nTask: {self.description['name']}, split: {eval_split}, language: {lang}. Running...")
                scores[lang] = self._evaluate_monolingual(model, self.dataset[lang], eval_split, train_split)
        else:
            scores = self._evaluate_monolingual(model, self.dataset, eval_split, train_split)

        if self.description["main_score"] in scores:
            scores["main_score"] = scores[self.description["main_score"]]
        else:
            print(f"WARNING: main score {self.description['main_score']} not found in scores {scores.keys()}")

        return scores

    def _evaluate_monolingual(self, model, dataset, eval_split="test", train_split="train"):
        train_split = dataset[train_split]
        eval_split = dataset[eval_split]

        logging.getLogger("sentence_transformers.evaluation.kNNClassificationEvaluator").setLevel(logging.WARN)
        if self.method == "kNN":
            evaluator = kNNClassificationEvaluator(
                train_split["text"], train_split["label"], eval_split["text"], eval_split["label"], k=self.k
            )
        elif self.method == "kNN-pytorch":
            evaluator = kNNClassificationEvaluatorPytorch(
                train_split["text"], train_split["label"], eval_split["text"], eval_split["label"], k=self.k
            )
        elif self.method == "logReg":
            evaluator = logRegClassificationEvaluator(
                train_split["text"], train_split["label"], eval_split["text"], eval_split["label"]
            )
        else:
            raise ValueError(f"Method {self.method} not supported")
        scores = evaluator(model)
        return scores
