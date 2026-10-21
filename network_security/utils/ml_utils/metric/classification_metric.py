
import sys

from sklearn.metrics import (
    f1_score,
    recall_score,
    precision_score,
    accuracy_score
)

from network_security.exception.exception import NetworkSecurityException

from network_security.entity.artifact_entity import (
    ClassificationMetricArtifact
)


def get_classification_score(y_true, y_pred):
    try:
        model_f1_score = f1_score(
            y_true=y_true,
            y_pred=y_pred,
            average="weighted",
            zero_division=0
        )

        model_recall_score = recall_score(
            y_true=y_true,
            y_pred=y_pred,
            average="weighted",
            zero_division=0
        )

        model_precision_score = precision_score(
            y_true=y_true,
            y_pred=y_pred,
            average="weighted",
            zero_division=0
        )

        model_accuracy_score = accuracy_score(
            y_true=y_true,
            y_pred=y_pred
        )

        return ClassificationMetricArtifact(
            f1_score=model_f1_score,
            recall_score=model_recall_score,
            precision_score=model_precision_score,
            accuracy_score=model_accuracy_score
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
