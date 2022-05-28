
# Infinite wordle (no guess limit)
# select a random five letter secret word that is not a title (a name)
# keep asking the user for a valid guess (5 letters)
# display scored guess
# display scored keyboard
# quit on empty guess input
# when secret is found, ask to continue
# if yes start over
# if no - dump game stats and quit
#
# TODO Next:
# 1 total game score (user : computer),
# 2 clear terminal between guesses and display full history each time
# 3 duplicate letters
#   when a letter is present in the word twice then colorize at most two duplicate letters in the guess
#   if three letters - colorize at most three
#
# remember all guesses and scores
#
# once user guesses secret start over:
# select new random secret and clear all previous data
#
# colorize user guess and display it
#   walk the five letter index
#     check secret word,
#     check the user guess
#       when letter is a hit in the correct position colorize it green,
#         keep score: 1
#       when letter is a hit in a wrong position colorize it orange,
#         keep score: 0
#       when letter is a miss colorize it red,
#         keep score: -1
#
#  colorize the keyboard in the same manner and display it
#
# 
# score keeping + colors
#    keep a list of five scores (0-4), the array index represents letter index in the word
#    walk the user guess and the score list and colorize user guess for output
#      walk the keyboard,
#        walk the user guess,
#          walk the score list
#            colorize each keyboard letter for output
#
# return to user for next guess

import random
from nltk.corpus import words
from nltk.tag import pos_tag
from os import system

class letter_color:
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   END = '\033[0m'
   
class letter_score:
    HIT = 'green'
    MISS = 'yellow'
    RED = 'red'
    
print(" Welcome to infinite wordle!")
print(" Type five letter guesses to play")
print(" Hit enter to quit")

wordlist = words.words()

keyboard = [['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l'],
            ['z','x','c','v','b','n','m']]

guesses_scores = []

# colorize letter
def colorize_letter (letter, color):
    if ( letter_score.RED == color ):
        return color.RED + letter + color.END
    if ( letter_score.MISS = color ):
        return color.YELLOW + letter + color.END
    if ( letter_score.HIT == color ):
        return color.GREEN + letter + color.END
        
    
# walk the list of scored guesses
#   walk keyboard letters by row
#     color keyboard letters
def show_colorized_keyboard ( guesses_scores ):
    colorized_keyboard = []
    for ( guess, score ) in guesses_scores:
        colorized_keyboard_row = []
        for keyboard_row in keyboard:
            for letter in keyboard_row:
                for i in range ( len ( score ) ):
                    if score [ i ] == '1' and letter == guess [ i ]:
                        colorized_keyboard_row.append ( colorize_letter ( letter, letter_score.HIT ) )
                        
                
def print_guess ( guesses_scores ):
    ( guess_word, score ) = guesses_scores [ -1 ]
    guess_word_letters = list ( guess_word )
    for i in range ( len ( score ) ):
        if score [ i ] == 0:
            print ( color.RED + guess_word_letters[i] + color.END, end = ' ' )
        if score [ i ] == 1:
            print ( color.YELLOW + guess_word_letters[i] + color.END, end = ' ' )
        if score [ i ] == 2:
            print ( color.GREEN + guess_word_letters[i] + color.END, end = ' ' ) 
    print()

       
counter = 0
random_word = random.choice ( wordlist ) 
while ( len ( random_word ) != 5 or random_word.istitle() ):
    counter += 1
    random_word = random.choice ( wordlist )

random_word_letters = list ( random_word )
print ( random_word_letters) 

score = [ 0,0,0,0,0 ]
while 0 in score or 1 in score:
    guess_word = input ( "Guess a five letter word: " )
    if guess_word == '':
        print ( "The secret was: ", random_word_letters )
        print ( "Bye!" )
        exit()
    
    while ( len ( guess_word ) != 5 or guess_word not in wordlist or guess_word.istitle () ):
        print ( "Please type a valid 5 letter word" )
        guess_word = input ( "Try again: " )
    
    guess_word_letters = list ( guess_word )
    score = [ 0, 0, 0, 0, 0 ]
    for i in range ( 5 ):
        if guess_word_letters [ i ] == random_word_letters [ i ]:
            score [ i ] = 2
        elif guess_word_letters [ i ] in random_word_letters:
            score [ i ] = 1
        else:
            score [ i ] = 0
    guess = ( guess_word, score ) 
    guesses.append ( guess )
    print_guess ( guesses )
    print_alphabet ( guesses )

#system('clear')

    
        
    
