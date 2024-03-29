import json
import math
import os
import pickle
import sys

import pandas as pd
from sklearn import metrics
from sklearn import tree
from dvclive import Live
from matplotlib import pyplot as plt
import yaml
from sklearn import preprocessing 


def evaluate(param_yaml_path, model, data, data_category, live):
    with open(param_yaml_path) as yaml_file:
        param_yaml = yaml.safe_load(yaml_file)
    target = [param_yaml["base"]["target_col"]]
    y = data[target]
    
    X = data.drop(target, axis=1)

    predictions_by_class = model.predict_proba(X)
 
    y_pred = model.predict(X)
 
    predictions = predictions_by_class[:, 1]


  

    # Use dvclive to log a few simple metrics...
    avg_prec = metrics.average_precision_score(y['diagnosis'].values, predictions)
    roc_auc = metrics.roc_auc_score(y, predictions)
    if not live.summary:
        live.summary = {"avg_prec": {}, "roc_auc": {}}
    live.summary["avg_prec"][data_category] = avg_prec
    live.summary["roc_auc"][data_category] = roc_auc

    # ... and plots...
    live.log_sklearn_plot("roc", y, predictions, name=f"roc/{data_category}")

    precision, recall, prc_thresholds = \
            metrics.precision_recall_curve(y, predictions)
    nth_point = math.ceil(len(prc_thresholds) / 1000)
    prc_points = list(zip(precision, recall, prc_thresholds))[::nth_point]
    prc_dir = os.path.join("eval", "prc")
    os.makedirs(prc_dir, exist_ok=True)
    prc_file = os.path.join(prc_dir, f"{data_category}.json")
    with open(prc_file, "w") as fd:
        json.dump(
            {
                "prc": [
                    {"precision": p, "recall": r, "threshold": t}
                    for p, r, t in prc_points
                ]
            },
            fd,
            indent=4,
        )

    # ... confusion matrix plot
    live.log_sklearn_plot("confusion_matrix",
                          y.squeeze(),
                          predictions_by_class.argmax(-1),
                          name=f"cm/{data_category}"
                         )
    
    return ""

if __name__=="__main__":
    # Load model and data.
    param_yaml_path = "params.yaml"
    with open(param_yaml_path) as yaml_file:
        param_yaml = yaml.safe_load(yaml_file)
    
    model_dir = param_yaml["model_dir"]
    with open(model_dir+"/model.pkl", "rb") as f:
        model = pickle.load(f)

    final_train_data_path = os.path.join(param_yaml["process"]["dir"], param_yaml["process"]["train_file"])
    train = pd.read_csv(final_train_data_path)

    final_test_data_path = os.path.join(param_yaml["process"]["dir"], param_yaml["process"]["test_file"])
    test = pd.read_csv(final_test_data_path)

    # Evaluate train and test datasets.
    EVAL_PATH = "eval"
    live = Live(os.path.join(EVAL_PATH, "live"), dvcyaml=False)
    evaluate(param_yaml_path,model, train, "train", live)
    evaluate(param_yaml_path,model, test, "test", live)
    live.make_summary()

    # Dump feature importance image and show it with your plots.
    fig, axes = plt.subplots(dpi=100)
    fig.subplots_adjust(bottom=0.2, top=0.95)
    importances = model.feature_importances_
    X= train.drop('diagnosis', axis=1)
    feature_names = [f"feature {i}" for i in range(X.shape[1])]
    forest_importances = pd.Series(importances, index=feature_names).nlargest(n=30)
    axes.set_ylabel("Mean decrease in impurity")
    forest_importances.plot.bar(ax=axes)

    fig.savefig(os.path.join(EVAL_PATH, "importance.png"))

    
#######################################
# EVAL_PATH = "eval"


# if len(sys.argv) != 3:
#     sys.stderr.write("Arguments error. Usage:\n")
#     sys.stderr.write("\tpython evaluate.py model features\n")
#     sys.exit(1)

# model_file = sys.argv[1]
# train_file = os.path.join(sys.argv[2], "train.pkl")
# test_file = os.path.join(sys.argv[2], "test.pkl")


# def evaluate(model, matrix, split, live):
#     """Dump all evaluation metrics and plots for given datasets."""
#     labels = matrix[:, 1].toarray().astype(int)
#     x = matrix[:, 2:]

#     predictions_by_class = model.predict_proba(x)
#     predictions = predictions_by_class[:, 1]

#     # Use dvclive to log a few simple metrics...
#     avg_prec = metrics.average_precision_score(labels, predictions)
#     roc_auc = metrics.roc_auc_score(labels, predictions)
#     if not live.summary:
#         live.summary = {"avg_prec": {}, "roc_auc": {}}
#     live.summary["avg_prec"][split] = avg_prec
#     live.summary["roc_auc"][split] = roc_auc

#     # ... and plots...
#     live.log_sklearn_plot("roc", labels, predictions, name=f"roc/{split}")

#     # ... but actually it can be done with dumping data points into a file:
#     # ROC has a drop_intermediate arg that reduces the number of points.
#     # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html#sklearn.metrics.roc_curve.
#     # PRC lacks this arg, so we manually reduce to 1000 points as a rough estimate.
#     precision, recall, prc_thresholds = \
#             metrics.precision_recall_curve(labels, predictions)
#     nth_point = math.ceil(len(prc_thresholds) / 1000)
#     prc_points = list(zip(precision, recall, prc_thresholds))[::nth_point]
#     prc_dir = os.path.join(EVAL_PATH, "prc")
#     os.makedirs(prc_dir, exist_ok=True)
#     prc_file = os.path.join(prc_dir, f"{split}.json")
#     with open(prc_file, "w") as fd:
#         json.dump(
#             {
#                 "prc": [
#                     {"precision": p, "recall": r, "threshold": t}
#                     for p, r, t in prc_points
#                 ]
#             },
#             fd,
#             indent=4,
#         )


#     # ... confusion matrix plot
#     live.log_sklearn_plot("confusion_matrix",
#                           labels.squeeze(),
#                           predictions_by_class.argmax(-1),
#                           name=f"cm/{split}"
#                          )


# # Load model and data.
# with open(model_file, "rb") as fd:
#     model = pickle.load(fd)

# with open(train_file, "rb") as fd:
#     train, feature_names = pickle.load(fd)

# with open(test_file, "rb") as fd:
#     test, _ = pickle.load(fd)

# # Evaluate train and test datasets.
# live = Live(os.path.join(EVAL_PATH, "live"), dvcyaml=False)
# evaluate(model, train, "train", live)
# evaluate(model, test, "test", live)
# live.make_summary()

# # Dump feature importance image and show it with your plots.
# fig, axes = plt.subplots(dpi=100)
# fig.subplots_adjust(bottom=0.2, top=0.95)
# importances = model.feature_importances_
# forest_importances = pd.Series(importances, index=feature_names).nlargest(n=30)
# axes.set_ylabel("Mean decrease in impurity")
# forest_importances.plot.bar(ax=axes)
# fig.savefig(os.path.join(EVAL_PATH, "importance.png"))
