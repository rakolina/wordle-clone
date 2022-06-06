# OPEN WORDLE
# (no daily limit)

# Select a random five letter secret word that is not a title or a name
# Ignore case - bring all words to lower case
# Keep asking the user for a valid guess (5 letters)
# Display scored/colorized guess
# Display scored/colorized keyboard
# When the secret is found, ask to continue
#   If yes start over
#   If no - dump game stats and quit
#
# TODO Next
# Clear terminal between guesses and display full history each time
# Duplicated letters in secret word
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
#    keep a list of five scores (array indexes 0-4), the array index represents letter index in the word
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

WORD_LENGTH = 5
DEBUG = 1


class Colorize:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


class Score:
    HIT = 2
    MISS = 1
    FAIL = 0


ALL_WORDS = words.words ( )

KEYBOARD = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

# keep total game score across all games
global user_score
user_score = 0
global robot_score
robot_score = 0


# colorize letter
def show_colorized_guess ( guess, score ):
    for i in range ( WORD_LENGTH ):
        if Score.HIT == score [ i ]:
            print ( Colorize.GREEN + guess [ i ] + Colorize.END, end = " " )
        elif Score.MISS == score [ i ]:
            print ( Colorize.YELLOW + guess [ i ] + Colorize.END, end = " " )
        elif Score.FAIL == score [ i ]:
            print ( Colorize.RED + guess [ i ] + Colorize.END, end = " " )
        else:
            print ( "Something went very wrong in show colorized guess method" )
            quit ( )

    # newline after word
    print ( )


# colorize letters green and orange based only on the latest guess
# colorize red based on all of the guesses
# Example guesses entry: { 'guess' : { 0:1, 1:0, 2:0, 3:0, 4:0 } }
# TODO better letter score lookup to colorize the keyboard
def show_colorized_keyboard ( secret, guesses ):
    if not secret or not guesses:
        print ( "Something is very wrong in show colorized keyboard" )
        quit ( )

    total_letter_scores = { }
    for guess in guesses:
        for i in range ( WORD_LENGTH ):
            guess_letter = guess [ i ]
            if guess_letter not in total_letter_scores:
                total_letter_scores [ guess_letter ] = guesses [ guess ] [ i ]
            else:
                if total_letter_scores [ guess_letter ] < guesses [ guess ] [ i ]:
                    total_letter_scores [ guess_letter ] = guesses [ guess ] [ i ]

    # colorized_keyboard = [ ]
    for keyboard_row in KEYBOARD:
        colorized_keyboard_row = [ ]
        for keyboard_letter in keyboard_row:
            if keyboard_letter not in total_letter_scores.keys( ):
                colorized_keyboard_row.append ( keyboard_letter )
            elif total_letter_scores [ keyboard_letter ] == Score.HIT:
                colorized_keyboard_row.append ( Colorize.GREEN + keyboard_letter + Colorize.END )
            elif total_letter_scores [ keyboard_letter ] == Score.MISS:
                colorized_keyboard_row.append ( Colorize.YELLOW + keyboard_letter + Colorize.END )
            elif total_letter_scores [ keyboard_letter ] == Score.FAIL:
                colorized_keyboard_row.append ( Colorize.RED + keyboard_letter + Colorize.END )

        display_offset = False
        for letter in colorized_keyboard_row:
            if 10 > len ( colorized_keyboard_row ) and not display_offset:
                display_offset = True
                for i in range ( 10 - len ( colorized_keyboard_row ) ):
                    print ( " ", end = "" )
            print ( letter, end = " " )

        print ( )


# select a random five letter secret
# take it down to lower case, even though likely the NLTK data set is already lower case
# keep count how many tries to find it in the NLP data struct            
def pick_secret_word ():
    counter = 0
    if 1 == DEBUG:
        # return "aurei"
        return "train"  # "ourie"

    secret_word = random.choice ( ALL_WORDS )
    while len ( secret_word ) != 5 or secret_word.istitle ( ):
        counter += 1
        secret_word = random.choice ( ALL_WORDS )

    print ( "Stats for nerds: picking a secret took ", counter, " tries" )
    return secret_word.lower ( )


# handle duplicated letters - version 2
# create a count of dupes and subtract from it when coloring
# avoid coloring too many/too few matched duplicates
def score_one_guess ( secret_word, guess_word ):
    letter_occurrence = { }

    if not secret_word or not guess_word:
        print ( "Something is very wrong in score one guess method" )
        quit ( )

    for i in range ( WORD_LENGTH ):
        if secret_word [ i ] not in letter_occurrence:
            letter_occurrence [ secret_word [ i ] ] = 1
        else:
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] + 1

    user_guess_score = { }
    for i in range ( WORD_LENGTH ):
        if secret_word [ i ] == guess_word [ i ] and letter_occurrence [ secret_word [ i ] ] > 0:
            user_guess_score [ i ] = Score.HIT
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] - 1
        elif guess_word [ i ] in secret_word and letter_occurrence [ secret_word [ i ] ] > 0:
            user_guess_score [ i ] = Score.MISS
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] - 1
        else:
            user_guess_score [ i ] = Score.FAIL

    return user_guess_score


# user guessed secret - increment user score
def is_game_over ( secret, guess ):
    if not secret:
        print ( "Something went very wrong in is game over method" )
        quit ( )

    game_over = secret == guess
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

    while WORD_LENGTH != len ( guess_word ) or guess_word not in ALL_WORDS or guess_word.istitle ( ):
        guess_word = input ( "Try again: " )

    return guess_word


def show_word ( word ):
    if word and WORD_LENGTH == len ( word ):
        return list ( word )
    else:
        print ( "Something is very wrong in show word function" )
        quit ( )


# store scored guesses in a dictionary with guess word as key and list of scores by letter index as value
# python dictionary keys are ordered as of python 3.6 (3.7)
# This is against the principle of a set (unordered!), but it is very useful to have this additional index
def display_game_stats ( secret, guesses ):
    # show as a list of letters
    if not secret or not guesses:
        print ( "Something is very wrong in display game stats method" )
        quit ( )

    print ( "Secret:  ", show_word ( secret ) )
    print ( "Guess:   ", show_word ( list ( guesses ) [ -1 ] ) )
    last_key = list ( guesses ) [ -1 ]
    # last added dictionary key is our current user guess
    show_colorized_guess ( last_key, guesses [ last_key ] )
    show_colorized_keyboard ( secret, guesses )


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

    scored_guesses = { }
    user_guess = ""
    game_secret = pick_secret_word ( )

    while not is_game_over ( game_secret, user_guess ):
        user_guess = ask_user_for_guess ( )
        scored_guesses [ user_guess ] = score_one_guess ( game_secret, user_guess )
        display_game_stats ( game_secret, scored_guesses )

    if not user_wants_to_continue ( ):
        finish ( )

################################################################
################################################################
################################################################
