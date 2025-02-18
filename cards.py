import random

def create_board(size=4):
    """Erstellt ein Spielfeld mit zufälligen Kartenpaaren"""
    num_pairs = (size*size) // 2
    cards = list(range(1, num_pairs +1)) * 2 # Jedes Paar kommt zweimal vor
    random.shuffle(cards) #Karten mischen
    return [cards[i * size: (i+1) * size] for i in range(size)]

