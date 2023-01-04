WORST_TIME = 1000
DIFFICULTIES = ["Easy", "Medium", "Hard"]

def read_high_scores(file):
    f = open(file)
    scores = {}
    lines = f.readlines()
    for line in lines:
        info = line.rstrip('\n').split(', ')
        scores[info[0]] = int(info[1])
    f.close()
    return scores 
        
def write_high_scores(scores, file):
    f = open(file, "w")
    for key, value in scores.items():
        f.write(key + ", " + str(value) + "\n")
    
def reset_high_scores(file):
    f = open(file, "w")
    for difficulty in DIFFICULTIES:
        f.write(difficulty + ", " + str(WORST_TIME) + "\n")