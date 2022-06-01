# INFINITE WORDLE
# (no daily limit)

# Select a random five letter secret word that is not a title or a name
# Ignore case - bring all words to lower case
# Keep asking the user for a valid guess (5 letters)
# Display scored/colorized guess
# Display scored/colorized keyboard
# Ask to quit on empty user input
# When the secret is found, ask to continue
# If yes start over
# If no - dump game stats and quit
#
# TODO Next
# Clear terminal between guesses and display full history each time
# Duplicate letters
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

MAX = 5


class Colorize:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

class Score:
    HIT = 2
    MISS = 1
    FAIL = 0

wordlist = words.words ( )

KEYBOARD = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

# remember all user guesses in current round
global user_guesses
user_guesses = [ ]

# keep total game score across all games
global user_score
user_score = 0
global robot_score
robot_score = 0


# colorize letter
def colorize_one_letter ( letter, score ):
    if Score.FAIL == score:
        return Colorize.RED + letter + Colorize.END
    elif Score.MISS == score:
        return Colorize.YELLOW + letter + Colorize.END
    elif Score.HIT == score:
        return Colorize.GREEN + letter + CoColorizelor.END
    else:
        print ( "Something is very wrong in colorize one letter method" )
        quit ( )

# walk keyboard rows
#   walk letters in keyboard row
#     colorize keyboard letters
#       walk the list of guesses
def show_colorized_keyboard ( secret_word, scored_guesses ):

    if not secret_word or not scored_guesses:
        print ( "Something is very wrong in show colorized keyboard" )
        quit ( )

    colorized_keyboard = [ ]
    for keyboard_row in KEYBOARD:
        colorized_keyboard_row = [ ]
        for keyboard_letter in keyboard_row:
            for guess in user_guesses:
                for guess_letter in guess:
                    if ( keyboard_letter == guess_letter ):
                        quit ( )
        #   colorized_keyboard_row.append ( colorize_letter ( letter, letter_score.HIT ) )
        # colorized_keyboard.insert ( colorized_keyboard_row )


# select a random five letter secret
# take it down to lower case, even though likely the NLTK data set is already lower case
# keep count how many tries to find it in the NLP data struct            
def pick_secret_word ():
    counter = 0
    secret_word = random.choice ( wordlist )
    while len ( secret_word ) != 5 or secret_word.istitle ( ):
        counter += 1
        secret_word = random.choice ( wordlist )

    print ( "Stats for nerds: picking a secret took ", counter, " tries" )
    return secret_word.lower ( )


# handle duplicated letters - version 2
def score_one_guess ( secret_word, guess_word ):

    letter_occurence = { }

    if not secret_word or not guess_word:
        print ( "Something is very wrong in score one guess method" )
        quit ( )

    for i in range ( MAX ):
        if secret_word [ i ] not in letter_occurence:
            letter_occurence [ secret_word [ i ] ] = 1
        else:
            letter_occurence [ secret_word [ i ] ] = letter_occurence [ secret_word [ i ] ] + 1

    user_guess_score = { }
    for i in range ( MAX ):
        if secret_word [ i ] == guess_word [ i ] and letter_occurence [ secret_word [ i ] ] > 0:
            user_guess_score [ i ] = Score.HIT
            letter_occurence [ secret_word [ i ] ] = letter_occurence [ secret_word [ i ] ] - 1
        elif guess_word [ i ] in secret_word and letter_occurence [ i ] > 0:
            user_guess_score [ i ] = Score.MISS
            letter_occurence [ secret_word [ i ] ] = letter_occurence [ secret_word [ i ] ] - 1
        else:
            user_guess_score [ i ] = Score.FAIL

    return user_guess_score


# user guessed secret - increment user score
def is_game_over ( secret_word, user_guess ):
    game_over = ( secret_word and user_guess and secret_word == user_guess )
    if game_over:
        global user_score
        user_score = user_score + 1
    return game_over


# when user enters empty word score goes to robot
def ask_user_for_guess ():
    guess_word = input ( "Your guess: " ).lower ( )
    if not guess_word:
        global robot_score
        robot_score = robot_score + 1
        if not user_wants_to_continue ( ):
            finish ( )

    while MAX != len ( guess_word ) or guess_word not in wordlist or guess_word.istitle ( ):
        guess_word = input ( "Try again: " )

    return guess_word


def show_word ( word ):
    if word and MAX == len ( word ):
        return list ( word )
    else:
        print ( "Something is very wrong in show word function" )
        quit ( )

def display_game_stats ( secret_word, scored_guesses ):
    # show as a list of letters
    if not secret_word or not scored_guesses:
        print ( "Something is very wrong in display game stats method" )
        quit ( )

    # print ( "Secret:  ", show_word ( secret_word ) )
    # print ( "Guess:   ", show_word ( guess_word ) )
    # show_colorized_keyboard ( secret_word, guesses )


def user_wants_to_continue ():
    continue_game = input ( "Again? (y)/n: " )
    return continue_game in [ "", "Y", "y" ]


def finish ():
    if user_score > robot_score:
        print ( "You won!" )
    elif user_score == robot_score:
        print ( "It is a tie!" )
    else:
        print ( "You lost." )
    print ( "Game score: ", user_score, ":", robot_score )
    print ( "Bye! Play again soon!" )
    quit ( )


################################################################
############################# MAIN #############################
################################################################

print ( "Welcome to infinite wordle!" )
while True:

    all_guesses = { }
    user_guess = ""
    game_secret = pick_secret_word ( )

    while not is_game_over ( game_secret, user_guess ):
        user_guess = ask_user_for_guess ( )
        all_guesses [ user_guess ] = score_one_guess ( game_secret, user_guess )
        display_game_stats ( game_secret, all_guesses )

    if not user_wants_to_continue ( ):
        finish ( )

################################################################
################################################################
################################################################

