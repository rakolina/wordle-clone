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

MAX = 5


class letter_color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


# class letter_score:
#     HIT = 'green'
#     MISS = 'yellow'
#     RED = 'red'


wordlist = words.words ( )

KEYBOARD = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

# remmeber all user guesses in current round
global guesses
guesses = [ ]

# keep total score across all games
global user_score
user_score = 0
global robot_score
robot_score = 0


# colorize letter
def colorize_letter ( letter, color ):
    if ( letter_score.RED == color ):
        return color.RED + letter + color.END
    if ( letter_score.MISS == color ):
        return color.YELLOW + letter + color.END
    if ( letter_score.HIT == color ):
        return color.GREEN + letter + color.END



# walk keyboard rows
#   walk letters in keyboard row
#     colorize keyboard letters
#       walk the list of guesses
def show_colorized_keyboard ( secret_word, guesses ):

    if not secret_word or not guesses:
        print ( "Something is very wrong in show colorized keyboard" )
        quit ( )

    colorized_keyboard = [ ]
    for keyboard_row in KEYBOARD:
        colorized_keyboard_row = [ ]
        for keyboard_letter in keyboard_row:
            for guess in guesses:
                for guess_letter in guess:

          colorized_keyboard_row.append ( colorize_letter ( letter, letter_score.HIT ) )
        colorized_keyboard.insert ( colorized_keyboard_row )


# select a random five letter secret
# keep count how many tries to find it in the NLP data struct            
def pick_secret_word ():
    counter = 0
    secret_word = random.choice ( wordlist )
    while (len ( secret_word ) != 5 or secret_word.istitle ( )):
        counter += 1
        secret_word = random.choice ( wordlist )
    return secret_word


# user guessed secret - increment user score
def is_game_over ( secret_word, user_guess ):
    game_over = ( secret_word and user_guess and secret_word == user_guess )
    if game_over:
        global user_score
        user_score = user_score + 1
    return game_over


# when user enters empty word score goes to robot
def ask_user_for_guess ():
    guess_word = input ( "Your guess: " )
    if not guess_word:
        global robot_score
        robot_score = robot_score + 1
        if not user_wants_to_continue ( ):
            finish ( )

    while ( MAX != len ( guess_word ) or guess_word not in wordlist or guess_word.istitle ( ) ):
        guess_word = input ( "Try again: " )

    global guesses
    guesses.insert ( guess_word )
    return guess_word


def show_word ( word ):
    if ( word and MAX == len ( word ) ) :
        return list ( word )
    else:
        print ( "Something is very wrong in show word function" )
        quit ( )

def display_game_stats ( secret_word, guess_word ):
    # show as a list of letters
    if not secret_word or not guess_word:
        print ( "Something is very wrong" )
        quit ( )
    print ( "Secret:  ", show_word ( secret_word ) )
    print ( "Guess:   ", show_word ( guess_word ) )
    show_colorized_keyboard ( secret_word, guesses )


def user_wants_to_continue ():
    continue_game = input ( "Again? (y)/n: " )
    return continue_game in [ "", "Y", "y" ]


def finish ():
    if ( user_score > robot_score ):
        print ( "You won!" )
    elif ( user_score == robot_score ):
        print ( "It is a tie!" )
    else
        print ( "You lost." )
    print ( "Game score: ", user_score, ":", robot_score )
    print ( "Bye! Play again soon!" )
    quit ( )


################################################################
############################# MAIN #############################
################################################################

print ( "Welcome to infinite wordle!" )
while True:
    guesses = [ ]
    user_guess = ""
    secret_word = pick_secret_word ( )

    while not is_game_over ( secret_word, user_guess ):
        user_guess = ask_user_for_guess ( )
        display_game_stats ( secret_word, user_guess )

    if not user_wants_to_continue ( ):
        finish ( )

################################################################
################################################################
################################################################

