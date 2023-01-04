"""This module is used to read and write to the "cache/high_scores.txt"
file, which records the user's highest score in each of the three difficulty
modes "Easy", "Medium" and "Hard". 
"""

"""Global Variables:

WORST_TIME: The worst time possible. Note that it is not actually possible
            for the player to get a time of 1000 since the timer only goes 
            up to 999. See "dialog.py" for more explanation
DIFFICULTIES: The three possible difficulties of the game
"""

WORST_TIME = 1000
DIFFICULTIES = ["Easy", "Medium", "Hard"]

def read_high_scores(file):
    """Fetches rows from a file. Retrieves the rows of the file and formats 
    it into a dictionary. Assumes that the file is formatted as a set of 
    comma seperated values, and that each line has exactly two values

    Args:
        file -- A string; the filepath to the file to be read

    Returns:
        A dict mapping the first entry of each line to the second entry of each line 

    Raises:
        FileNotFoundError: No such file or directory
        IndexError: list index out of range
    """
    f = open(file)
    scores = {}
    lines = f.readlines()
    for line in lines:
        info = line.rstrip('\n').split(', ')
        scores[info[0]] = int(info[1])
    f.close()
    return scores 
        
def write_high_scores(scores, file):
    """Writes the scores to the file, following the format described for the 
    input in the read_high_scores method. 

    Args:
        scores -- A dictionary; a map between the difficulty and the user's best
        score in each category. 
        file -- A string; the filepath to the file to be written to

    Raises:
        FileNotFoundError: No such file or directory
        IndexError: list index out of range
    """
    f = open(file, "w")
    for key, value in scores.items():
        f.write(key + ", " + str(value) + "\n")
    
def reset_high_scores(file):
    """Sets the best score in each category equal to WORST_TIME, and writes
    to FILE. Note this function is unused by main. It exists only to reset
    the high scores file. 

    Args:
        file -- A string; the filepath to the file to be written to

    Raises:
        FileNotFoundError: No such file or directory
    """
    f = open(file, "w")
    for difficulty in DIFFICULTIES:
        f.write(difficulty + ", " + str(WORST_TIME) + "\n")