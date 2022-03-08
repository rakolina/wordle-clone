# import nltk;
# nltk.download('popular')
# from nltk.corpus import words
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
# print("all words: ", len(wordlist))

def colorize_letter(alphabet, letter, c):
    for l in range(len(alphabet)):
        if alphabet[l] == letter:
            alphabet[l] = c + alphabet[l] + color.END
            
    
alphabet = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m']
def print_alphabet(score):
    row1 = 10
    row2 = 19
    counter = 0
    for letter in alphabet:
        counter+=1
        print (letter, end=' ')
        if counter == row1 or counter == row2:
            print()
            
        
counter=0
random_word = random.choice(wordlist)
while (len(random_word) !=5 or random_word.istitle()):
    counter+=1
    random_word = random.choice(wordlist)

random_word_letters = list(random_word)
#print (random_word_letters)

score = ['0']
while '0' in score or '1' in score:
    guess_word = input("Guess a five letter word: ")
    while (len(guess_word) !=5 or guess_word not in wordlist):
        guess_word = input("Try again: ")
    
    guess_word_letters = list(guess_word)
    score = []
    for i in range(5):
        if guess_word_letters[i] == random_word_letters[i]:
            colorize_letter(alphabet, guess_word_letters[i], color.GREEN)
        elif guess_word_letters[i] in random_word_letters:
            colorize_letter(alphabet, guess_word_letters[i], color.YELLOW)
        else:
            if guess_word_letters[i] in alphabet:
                colorize_letter(alphabet, guess_word_letters[i], color.RED)

    print (guess_word_letters)
    print_alphabet(alphabet)

#system('clear')

    
        
    