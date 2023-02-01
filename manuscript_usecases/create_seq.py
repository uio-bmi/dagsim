import os
import pandas as pd

seed = 2
sequence_count = 2000
os.system(f"olga-generate_sequences --humanTRB -n {sequence_count} -o rep.tsv")  # --seed={seed}")

df = pd.read_csv('rep.tsv', sep='\\t', engine='python')

sequences = df.iloc[:, 1].values
sequences = sequences.tolist()

textfile = open("rep.txt", "w")
for element in sequences:
    textfile.write(element + "\n")
textfile.close()
