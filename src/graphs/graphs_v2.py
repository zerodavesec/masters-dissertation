import json
from decimal import Decimal

import numpy
import pandas as pd
from matplotlib import pyplot

from src.metrics.averages import Averages, AveragesDict, GroupedAveragesDict


def create_2d_graph(averages: AveragesDict, category: str):

    title: str = f"Rule performance per {category}"

    methods: list[str] = [key for key in averages]

    recall: list[float] = [float(averages[key]["recall"]) for key in averages]
    precision: list[float] = [float(averages[key]["precision"]) for key in averages]
    f1_score: list[float] = [float(averages[key]["f1_score"]) for key in averages]

    pyplot.style.use("seaborn-v0_8-whitegrid")

    colors = {
        "Recall": "#4E79A7",
        "Precision": "#F28E2B",
        "F1": "#59A14F",
    }

    bar_width = 0.18
    x = numpy.arange(len(methods))
    fig, ax = pyplot.subplots(figsize=(13, 7), constrained_layout=True)

    bars1 = ax.bar(
        x - bar_width - 0.01,
        recall,
        width=bar_width,
        color=colors["Recall"],
        label="Recall",
    )

    bars2 = ax.bar(
        x,
        precision,
        width=bar_width,
        color=colors["Precision"],
        label="Precision",
    )

    bars3 = ax.bar(
        x + bar_width + 0.01,
        f1_score,
        width=bar_width,
        color=colors["F1"],
        label="F1 Score",
    )

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt="%.3f", padding=4, fontsize=18, fontweight="bold")

    ax.set_ylim(0, 1.18)

    ax.set_ylabel("Metric Value", fontsize=20, fontweight="bold")

    ax.set_xlabel(f"{category}", fontsize=20, fontweight="bold")

    ax.set_xticks(x)
    methods = [
        method.title()
        .replace("Manual_Ai", "Manual-AI")
        .replace("Automated_Ai", "AI-Automated")
        for method in methods
    ]
    ax.set_xticklabels(methods, fontsize=20)

    ax.set_yticks(numpy.arange(0, 1.1, 0.1))
    ax.tick_params(axis="y", labelsize=11)

    ax.set_title(
        f"{title}",
        fontsize=25,
        fontweight="bold",
        pad=20,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.grid(axis="x", visible=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(ncol=3, frameon=False, fontsize=20, loc="upper right")

    pyplot.show()


def create_grouped_2d_graph_horizontal(
    data: GroupedAveragesDict, category: str = "Generation Method"
):
    rule_type_labels = {"detection": "Detection", "correlation": "Correlation"}
    keys: list[tuple[str, str]] = [
        (method, rule_type) for method in data for rule_type in data[method]
    ]
    block_labels: list[str] = [
        f"{method.replace('_', ' ').title()}\n{rule_type_labels[rule_type]}"
        for method, rule_type in keys
    ]
    recall: list[float] = [float(data[m][r]["recall"]) for m, r in keys]
    precision: list[float] = [float(data[m][r]["precision"]) for m, r in keys]
    f1_score: list[float] = [float(data[m][r]["f1_score"]) for m, r in keys]

    pyplot.style.use("seaborn-v0_8-whitegrid")
    colors = {
        "Recall": "#4E79A7",
        "Precision": "#F28E2B",
        "F1": "#59A14F",
    }
    bar_width = 0.2
    x = numpy.arange(len(block_labels))

    # Height doubled (7 -> 14) to give each category cluster room to breathe.
    fig, ax = pyplot.subplots(figsize=(15, 14), constrained_layout=True)

    bars1 = ax.barh(
        y=x + bar_width,
        width=recall,
        height=bar_width,
        color=colors["Recall"],
        label="Recall",
    )
    bars2 = ax.barh(
        y=x,
        width=precision,
        height=bar_width,
        color=colors["Precision"],
        label="Precision",
    )
    bars3 = ax.barh(
        y=x - bar_width,
        width=f1_score,
        height=bar_width,
        color=colors["F1"],
        label="F1 Score",
    )
    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt="%.3f", padding=4, fontsize=15, fontweight="bold")

    for i in range(2, len(block_labels), 2):
        ax.axhline(i - 0.5, color="grey", linestyle=":", linewidth=1, alpha=0.6)

    ax.set_xlim(0, 1.12)
    ax.set_xlabel("Metric Value", fontsize=20, fontweight="bold")
    ax.set_ylabel(f"Generation Method and Rule Type", fontsize=20, fontweight="bold")
    ax.set_yticks(x)
    ax.set_yticklabels(block_labels, fontsize=20)
    ax.set_xticks(numpy.arange(0, 1.1, 0.1))
    ax.tick_params(axis="x", labelsize=11)
    ax.set_title(
        f"Rule performance per generation method and rule type",
        fontsize=20,
        fontweight="bold",
        pad=20,
    )
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(ncol=3, frameon=False, fontsize=16, loc="lower right")

    ax.set_ylim(ax.get_ylim()[::-1])  # type: ignore
    # Axis inversion

    pyplot.show()


def create_grouped_2d_graph_vertical(data: GroupedAveragesDict, category: str = ""):
    rule_type_labels = {"detection": "Detection", "correlation": "Correlation"}

    keys: list[tuple[str, str]] = [
        (method, rule_type) for method in data for rule_type in data[method]
    ]

    block_labels: list[str] = [
        f"{method.replace('_', ' ').title()}\n{rule_type_labels[rule_type]}"
        for method, rule_type in keys
    ]

    recall: list[float] = [float(data[m][r]["recall"]) for m, r in keys]
    precision: list[float] = [float(data[m][r]["precision"]) for m, r in keys]
    f1_score: list[float] = [float(data[m][r]["f1_score"]) for m, r in keys]

    pyplot.style.use("seaborn-v0_8-whitegrid")
    colors = {
        "Recall": "#4E79A7",
        "Precision": "#F28E2B",
        "F1": "#59A14F",
    }
    bar_width = 0.26
    x = numpy.arange(len(block_labels))

    fig, ax = pyplot.subplots(figsize=(15, 7), constrained_layout=True)

    bars1 = ax.bar(
        x - bar_width,
        recall,
        width=bar_width,
        color=colors["Recall"],
        label="Recall",
    )
    bars2 = ax.bar(
        x,
        precision,
        width=bar_width,
        color=colors["Precision"],
        label="Precision",
    )
    bars3 = ax.bar(
        x + bar_width,
        f1_score,
        width=bar_width,
        color=colors["F1"],
        label="F1 Score",
    )

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=15, fontweight="bold")

    for i in range(2, len(block_labels), 2):
        ax.axvline(i - 0.5, color="grey", linestyle=":", linewidth=1, alpha=0.6)

    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Metric Value", fontsize=20, fontweight="bold")
    ax.set_xlabel(f"{category}", fontsize=20, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(block_labels, fontsize=20)
    ax.set_yticks(numpy.arange(0, 1.1, 0.1))
    ax.tick_params(axis="y", labelsize=11)
    ax.set_title(
        f"Macro average per {category}, split by rule type",
        fontsize=20,
        fontweight="bold",
        pad=20,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.grid(axis="x", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(ncol=3, frameon=False, fontsize=20, loc="upper right")
    pyplot.show()


if __name__ == "__main__":
    df = pd.read_csv("./results/Dissertation-Results.csv")
    averages = Averages(df)
    print(json.dumps(averages.targeted_testing_macro_average_gen_method, default=float))
    create_2d_graph(
        averages.targeted_testing_macro_average_gen_method,
        category="Authoring Method - Targeted Testing",
    )
    create_2d_graph(
        averages.non_targeted_testing_macro_average_gen_method,
        category="Authoring Method - Non-Targeted Testing",
    )

    create_2d_graph(
        averages.general_macro_average_gen_method, category="Authoring Method"
    )
    create_2d_graph(
        averages.targeted_testing_macro_average_rule_type,
        category="Rule Type - Targeted Testing",
    )
    create_2d_graph(
        averages.non_targeted_testing_macro_average_rule_type,
        category="Rule Type - Non-Targeted Testing",
    )

    # create_2d_graph(
    #     averages.general_macro_average_gen_method,
    #     category="Generation Method",
    # )
    create_2d_graph(
        averages.general_macro_average_rule_type,
        category="Rule Type - Non-Targeted Testing",
    )

    create_grouped_2d_graph_horizontal(
        averages.targeted_testing_macro_average_rule_type_and_gen_method
    )

    create_grouped_2d_graph_horizontal(
        averages.non_targeted_testing_macro_average_rule_type_and_gen_method
    )
    # create_grouped_2d_graph_vertical(
    # averages.general_macro_average_rule_type_and_gen_method
    # )
