import os
import glob
import numpy as np
import csv

#Property of LaunchEHD Limited 2026

KELLY_FRACTION = 0.5
KELLY_EDGE_THRESHOLD = 0.02

#it is really important to note that this script expects matricies expressed as probabilities

def load_model(path):
    matrix = np.loadtxt(path, delimiter=",")
    print(f"Loaded model matrix: shape {matrix.shape}")
    return matrix

def load_odds(folder):
    files = glob.glob(os.path.join(folder, "*.csv"))
    odds = {}
    for f in files:
        name = os.path.basename(f).replace(".csv", "")
        odds[name] = np.loadtxt(f, delimiter=",")
        print(f"Found '{name}': shape {odds[name].shape}")
    return odds

def fractional_kelly(model_prob, odds_prob, kelly_fraction, edge_threshold):
    #kelly for probabilities
    ev = (model_prob/odds_prob)-1  #p/q - 1
    if ev <= edge_threshold: #we dont want to bet when the edge is small
        return 0
    return (ev*kelly_fraction*odds_prob)/(1-odds_prob)  #f=k*(p-q)/(1-q)

def rank_bets(model, odds_dict, kelly_fraction, kelly_threshold):
    all_bets = []
    for bookie, odds_matrix in odds_dict.items():
        difference_matrix = model - odds_matrix
        n_rows, n_cols = difference_matrix.shape
        for y in range(n_rows):
            for x in range(n_cols):
                edge = difference_matrix[y, x]
                odds_prob = odds_matrix[y, x]
                model_prob = model[y, x]
                kelly = fractional_kelly(model_prob, odds_prob, kelly_fraction, kelly_threshold)
                all_bets.append({
                    "bookmaker": bookie,
                    "score": f"{x}-{y}",
                    #"model_prob": model[y, x],
                    #"odds_prob": odds_matrix[y, x]
                    "edge_prob": edge,
                    "derated_kelly_fraction": kelly
                })
    all_bets.sort(key=lambda bet: bet["edge_prob"], reverse=True)
    return all_bets

def save_ranked_bets(all_bets, filepath):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        if len(all_bets) > 0:
            fieldnames = all_bets[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_bets)
    return all_bets

prediction_matrix = load_model("outputs/lowscorecorrectedjointpmfmatrix.csv")
odds_dict = load_odds("inputdata")
ranked_bets = rank_bets(prediction_matrix, odds_dict, KELLY_FRACTION, KELLY_EDGE_THRESHOLD)
save_ranked_bets(ranked_bets, "outputs/ranked_bets.csv")

with open("outputs/ranked_bets.csv", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(','.join(row))