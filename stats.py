import sys
import csv
import re
from combo.predict import COMBO
import spacy
import os
import pathlib 
PATH ="C:\\Users\\Adam\\magisterka\\data"

import pandas as pd
import matplotlib.pyplot as plt

'''with open(r'C:\\Users\Adam\\magisterka\\data\\ENG\\eng.erst.gum_dev.conllu', "r", encoding="utf8") as data_file:
    with open(r'C:\\Users\Adam\\magisterka\\data\\ENG\\better.csv', "w", encoding="utf8", newline="") as new_file:
        reader = csv.reader(data_file, delimiter="\t")
        writer = csv.writer(new_file, delimiter="\t", )
        for row in reader:
            if row != []:
                #print(row)
                if row[0].isnumeric() and row[0] != "#":
                    writer.writerow(row)'''
column_names = ["id", "token", "lemma", "upostag", "some", "no", "gov", "deprel", "gov+deprel", "additional"]

df = pd.read_csv(r'C:\\Users\Adam\\magisterka\\data\\ENG\\better.csv', delimiter="\t", names=column_names)  # Replace with your actual file path

# 2. Add a new column to indicate presence of "Seg=B-seg"
df["has_B_seg"] = df["additional"].str.contains("Seg=B-seg", na=False)

# 3. Plot frequency of "Seg=B-seg" by different features
'''
# Helper function to make a count plot
def plot_seg_counts(column_name):
    count_df = df.groupby([column_name, "has_B_seg"]).size().unstack(fill_value=0)

    # Plot
    ax = count_df.plot(kind="bar", figsize=(10, 5))
    ax.set_title(f'"Seg=B-seg" counts by {column_name}')
    ax.set_ylabel("Count")
    ax.set_xlabel(column_name)
    ax.legend(["No Seg=B-seg", "Has Seg=B-seg"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
# 4. Create plots
plot_seg_counts("upostag")
plot_seg_counts("deprel")'''
df_melted = pd.melt(
    df,
    id_vars=["has_B_seg"],
    value_vars=["upostag", "deprel"],
    var_name="feature_type",
    value_name="category"
)

# Group and calculate % with Seg=B-seg
grouped = df_melted.groupby(["feature_type", "category", "has_B_seg"]).size().unstack(fill_value=0)
percentages = (grouped.div(grouped.sum(axis=1), axis=0) * 100)[True]  # Only keep the % with Seg=B-seg
row_counts = grouped.sum(axis=1)

# Optional: drop specific X-axis values (e.g., punctuation or irrelevant labels)
# Example: remove "PUNCT" and "SYM" from upostag and "punct" from deprel
percentages = percentages[row_counts > 10]


# Plot
fig, ax = plt.subplots(figsize=(14, 6))

x_labels = [f"{ftype}:{cat}" for ftype, cat in percentages.index]
x_pos = range(len(percentages))

# Plot only % with Seg=B-seg
ax.bar(x_pos, percentages.values, color="skyblue")

# Formatting
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels, rotation=45, ha="right")
ax.set_ylabel("Percentage of Seg=B-seg (%)")
ax.set_title('Percentage of "Seg=B-seg" by upostag and deprel')
plt.tight_layout()
plt.show()

