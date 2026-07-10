import os
import glob
import numpy as np
import csv

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

def rank_bets(model, odds):
    all_bets = []
    
    for bookie, odds_matrix in odds.items():
        difference_matrix = model - odds_matrix
        
        n_rows, n_cols = difference_matrix.shape
        for y in range(n_rows):
            for x in range(n_cols):
                edge = difference_matrix[y, x]
                all_bets.append({
                    "bookmaker": bookie,
                    "score": f"{x}-{y}",
                    "edge": edge,
                    "model_prob": model[y, x],
                    "odds_prob": odds_matrix[y, x]
                })
    
    all_bets.sort(key=lambda bet: bet["edge"], reverse=True)
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
ranked_bets = rank_bets(prediction_matrix, odds_dict)
save_ranked_bets(ranked_bets, "outputs/ranked_bets.csv")
print(ranked_bets)
