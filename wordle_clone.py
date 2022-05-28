# Infinite wordle (no daily limit)
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

import random, nltk
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


wordlist = words.words ( )

keyboard = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

guesses_scores = [ ]


# colorize letter
def colorize_letter ( letter, color ):
    if ( letter_score.RED == color ):
        return color.RED + letter + color.END
    if ( letter_score.MISS == color ):
        return color.YELLOW + letter + color.END
    if ( letter_score.HIT == color ):
        return color.GREEN + letter + color.END


# walk the list of scored guesses
#   walk keyboard letters by row
#     color keyboard letters
def show_colorized_keyboard ( guesses_scores ):
    colorized_keyboard = [ ]
    for ( guess, score ) in guesses_scores:
        colorized_keyboard_row = [ ]
        for keyboard_row in keyboard:
            for letter in keyboard_row:
                for i in range ( len ( score ) ):
                    if score [ i ] == '1' and letter == guess [ i ]:
                        colorized_keyboard_row.append ( colorize_letter ( letter, letter_score.HIT ) )


# select a random five letter secret
# keep count how many tries to find it in the NLP data struct            
def pick_secret_word ():
    counter = 0
    secret_word = random.choice ( wordlist )
    while (len ( secret_word ) != 5 or secret_word.istitle ( )):
        counter += 1
        secret_word = random.choice ( wordlist )
    return secret_word


def is_game_over ( secret_word, user_guess ):
    game_over = ( secret_word and user_guess and secret_word == user_guess )
    return game_over


def ask_user_for_guess ():
    guess_word = input ( "Your guess: " )
    if not guess_word:
        if not does_user_want_to_continue ( ):
            finish ( )

    while ( 5 != len ( guess_word ) or guess_word not in wordlist or guess_word.istitle ( ) ):
        guess_word = input ( "Try again: " )
    return guess_word


def show_word ( word ):
    if word and 0 < len ( word ):
        return list ( word )
    else:
        return []

def display_game_stats ( secret_word, guess_word ):
    # show as a list of letters
    if not secret_word or not guess_word:
        print ( "Something is very wrong" )
        exit ( )
    print ( show_word ( secret_word ) )
    print ( show_word( guess_word ) )


def user_wants_to_continue ():
    continue_game = input ( "Continue? (Y): " )
    return continue_game in [ "", "Y", "y" ]


def finish ():

    print ( "Game score: ", user_score, ":", robot_score )
    quit ( )


################################################################
############################# MAIN #############################
################################################################

print ( " Welcome to infinite wordle!" )

guesses = [ ]
user_score = 0
robot_score = 0

while True:
    secret_word = pick_secret_word ( )
    user_guess = ""
    while not is_game_over( secret_word, user_guess ):
        user_guess = ask_user_for_guess ( )
        display_game_stats ( secret_word, user_guess )
    if not user_wants_to_continue ( ):
        finish ( )

################################################################
################################################################
################################################################


# make a list of letters
secret_word_letters = list ( secret_word )
print ( secret_word_letters )

score = [ 0, 0, 0, 0, 0 ]
while 0 in score or 1 in score:
    guess_word = input ( "Guess a five letter word: " )
    if guess_word == '':
        print ( "The secret was: ", random_word_letters )
        print ( "Bye!" )
        exit ( )

    while (len ( guess_word ) != 5 or guess_word not in wordlist or guess_word.istitle ( )):
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
