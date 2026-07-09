import os
import glob
import numpy as np

def load_model():
    path = "outputs/lowscorecorrectedjointpmfmatrix.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    matrix = np.loadtxt(path, delimiter=",")
    print(f"Loaded model matrix: shape {matrix.shape}")
    return matrix

def load_odds(folder="inputdata"):
    files = glob.glob(os.path.join(folder, "*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder}")
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
                    "result": f"{x}-{y}",
                    "edge": edge,
                    "model_prob": model[y, x],
                    "odds_prob": odds_matrix[y, x]
                })
    
    all_bets.sort(key=lambda bet: bet["edge"], reverse=True)
    return all_bets

def save_ranked_bets(all_bets, folder="outputs", filename="ranked_bets.csv"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    
    df = pd.DataFrame(all_bets)
    df.to_csv(file_path, index=False)
    print(f"\nSaved ranked bets to: {file_path}")
    print(f"Total bets ranked: {len(all_bets)}")
    return df