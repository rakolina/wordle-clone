
# select a random five letter word that is not a title (a name)
# ask user for a guess
# colorize the guess and display it
#   when letter is a hit in correcdt position colorize green
#   when letter is a hit in a wrong position colorize orange
#   when letter is a miss colorize red
#
# score keeping:
#    
# return to user for next guess





import random
from nltk.corpus import words
from nltk.tag import pos_tag
from os import system

class color:
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   END = '\033[0m'
   

wordlist = words.words()
alphabet = ['q','w','e','r','t','y','u','i','o','p',
            'a','s','d','f','g','h','j','k','l',
            'z','x','c','v','b','n','m']
guesses = []

def print_alphabet (guesses):
    for (guess, score) in guesses:
        for s in range (len (score)):
            if s == '0':
                


def print_guess (guesses):
    (guess_word, score) = guesses [-1]
    guess_word_letters = list (guess_word)
    for i in range (5):
        if score[i] == 0:
            print (color.RED + guess_word_letters[i] + color.END, end = ' ')
        if score[i] == 1:
            print (color.YELLOW + guess_word_letters[i] + color.END, end = ' ')
        if score[i] == 2:
            print (color.GREEN + guess_word_letters[i] + color.END, end = ' ')
    print()

       
counter = 0
random_word = random.choice (wordlist)
while (len (random_word) !=5 or random_word.istitle()):
    counter += 1
    random_word = random.choice (wordlist)

random_word_letters = list (random_word)
print (random_word_letters)

score = [0,0,0,0,0]
while 0 in score or 1 in score:
    guess_word = input("Guess a five letter word: ")
    if guess_word == '':
        print ("The word was: ", random_word_letters)
        print ("Bye")
        exit()
    
    while (len (guess_word) !=5 or guess_word not in wordlist):
        guess_word = input("Try again: ")
    
    guess_word_letters = list(guess_word)
    score = [0, 0, 0, 0, 0]
    for i in range(5):
        if guess_word_letters[i] == random_word_letters[i]:
            score[i] = 2
        elif guess_word_letters[i] in random_word_letters:
            score[i] = 1
        else:
            score[i] = 0
    guess = (guess_word, score)
    guesses.append (guess)
    print_guess (guesses)
    print_alphabet (guesses)

#system('clear')

    
        
    
