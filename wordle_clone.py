# OPEN WORDLE without a daily limit
#
# Select a random five letter secret word that is not a title or a proper name
# Ignore case - bring all words to lower case
# Keep asking the user for a valid guess (5 letters)
# Display scored/colorized guess
# Display scored/colorized keyboard
# When the secret is found, ask to continue
#   If yes start over
#   If no - dump game stats and quit
#
# Duplicated letters in secret word
#   when a letter is present in the word twice then colorize at most two duplicate letters in the guess
#   if three letters - colorize at most three
#
# TODOs
#    thread the abysmally slow wordnet lookup, display a UI indicator
#    thread secret word picking with UI progress indicator
#    Popup window UI instead of ASCII art in the terminal


import nltk
from nltk.corpus import words
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from os import system, name
from time import sleep
import random


DEBUG = 0


class Colorize:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


class Score:
    HIT = 2
    MISS = 1
    FAIL = 0


LETTER_PLACEHOLDER = "*"

KEYBOARD = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

# game score across all turns
global user_score
user_score = 0
global robot_score
robot_score = 0


def clear_terminal ():
    # windows
    if name == 'nt':
        _ = system ( 'cls' )
    # mac, linux
    else:
        _ = system ( 'clear' )


def show_colorized_guess ( guess, score ):
    colorized_guess = [ ]
    for i in range ( MAX_WORD_LENGTH ):
        if Score.HIT == score [ i ]:
            colorized_letter = Colorize.GREEN + guess [ i ] + Colorize.END
        elif Score.MISS == score [ i ]:
            colorized_letter = Colorize.YELLOW + guess [ i ] + Colorize.END
        elif Score.FAIL == score [ i ]:
            colorized_letter = Colorize.RED + guess [ i ] + Colorize.END
        else:
            print ( "Something went very wrong in show colorized guess method" )
            quit ( )
        colorized_guess.append ( colorized_letter )
        print ( colorized_letter, end = " " )

    print ( )

    return colorized_guess


# colorize letters green and orange based on the last guess
# colorize red based on all the guesses
def show_colorized_keyboard ( guesses = [ ] ):

    # previous guesses
    total_letter_scores = { }
    for guess, score in guesses [ : -1 ]:
        for i in range ( len ( guess ) ):
            guess_letter = guess [ i ]
            if 0 == score [ i ]:
                if guess_letter not in total_letter_scores:
                    total_letter_scores [ guess_letter ] = score [ i ]
                else:
                    if total_letter_scores [ guess_letter ] < score [ i ]:
                        total_letter_scores [ guess_letter ] = score [ i ]

    # latest guess overrides previous scores
    if not guesses:
        guess = ""
        score = [ ]
    else:
        guess, score = guesses [ -1 ]

    for i in range ( len ( guess ) ):
        guess_letter = guess [ i ]
        if guess_letter not in total_letter_scores:
            total_letter_scores [ guess_letter ] = score [ i ]
        else:
            if total_letter_scores [ guess_letter ] < score [ i ]:
                total_letter_scores [ guess_letter ] = score [ i ]

    print ( '-------------------' )
    for keyboard_row in KEYBOARD:
        colorized_keyboard_row = [ ]
        for keyboard_letter in keyboard_row:
            if keyboard_letter not in total_letter_scores.keys ( ):
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
                    print ( ' ', end = '' )
            print ( letter, end = ' ' )
        print ( )
    print ( '-------------------' )


# select a random five letter secret
# take it down to lower case, even though likely the NLTK data set is already lower case
def pick_secret_word ( words, lemmas, guesses ):

    if 0 != DEBUG:
        return "aurei"  # "ourie"

    secret_word = ""
    counter = 0
    while secret_word in guesses or secret_word.istitle ( ) or secret_word not in lemmas:
        secret_word = random.choice ( words )
        if 0 != DEBUG:
            print ( secret_word )
        counter += 1

    if 0 != DEBUG:
        show_count = Colorize.GREEN + str ( counter ) + Colorize.END
        print ( "Stats for nerds: picking a secret word took", show_count, "tries" )

    return secret_word.lower ( )


# handle duplicated letters - version 2
# create a count of dupes and subtract from it when coloring
# avoid coloring too many/too few matched duplicates
# return a 2d array [ 'guess word', [ score1, score2, ... score4 ] ]
def score_one_guess ( secret_word, guess_word ):
    if len ( secret_word ) != len ( guess_word ):
        print ( "Secret word and user guess are different length. Exit.")
        quit ( )

    letter_occurrence = { }
    for i in range ( len ( secret_word ) ):
        if secret_word [ i ] not in letter_occurrence:
            letter_occurrence [ secret_word [ i ] ] = 1
        else:
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] + 1

    scored_guess = [ guess_word ]
    user_guess_score = [ ]
    for i in range ( len ( secret_word ) ):
        if secret_word [ i ] == guess_word [ i ] and letter_occurrence [ secret_word [ i ] ] > 0:
            user_guess_score.insert ( i, Score.HIT )
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] - 1
        elif guess_word [ i ] in secret_word and letter_occurrence [ secret_word [ i ] ] > 0:
            user_guess_score.insert ( i, Score.MISS )
            letter_occurrence [ secret_word [ i ] ] = letter_occurrence [ secret_word [ i ] ] - 1
        else:
            user_guess_score.insert ( i, Score.FAIL )

    scored_guess.append ( user_guess_score )

    return scored_guess


# user guessed secret - increment user score
def is_game_over ( secret, guess, tries ):
    if secret == guess:
        global user_score
        user_score += 1

    elif len ( secret ) == tries:
        global robot_score
        robot_score += 1

    return secret == guess or len ( secret ) == tries


def ask_user_for_guess ( secret, words, lemmas ):
    guess_word = ""
    while len ( guess_word ) != len ( secret ) or guess_word not in words or guess_word.istitle ( ) or guess_word not in lemmas:
        guess_word = input ( "Your guess: " ).lower ( )

    return guess_word


# store scored guesses in a dictionary with guess word as key and list of scores by letter index as value
# python dictionary keys are ordered as of python 3.6 (3.7)
# This is against the principle of a set (unordered!), but it is very useful to have this additional index
def display_game_stats ( secret, guesses, history ):
    if 0 != DEBUG:
        print ( "Secret:  ", list ( secret ) )
        print ( "Guess:   ", list ( guesses [ -1 ] [ 0 ] ) )

    clear_terminal ( )
    display_guess_history ( len ( secret ), history )
    history.append ( show_colorized_guess ( guesses [ -1 ] [ 0 ], guesses [ -1 ] [ 1 ] ) )
    show_colorized_keyboard ( guesses )


def user_wants_to_continue ():
    continue_game = input ( "Play again? (y)/n: " )
    return continue_game in [ "", "Y", "y" ]


def finish ():
    clear_terminal ( )

    if user_score > robot_score:
        print ( "You won!" )
    elif user_score == robot_score:
        print ( "Game is a tie!" )
    else:
        print ( "You lost." )

    print ( "Game score", user_score, ":", robot_score )
    print ( "Play again soon!" )

    quit ( )


def display_game_banner ( ):
    print ( "---------------------------------------" )
    print ( "|                                     |" )
    print ( "|       WELCOME TO OPEN WORDLE!       |" )
    print ( "|                                     |" )
    print ( "---------------------------------------" )


def show_current_game ( secret, guesses = [ ], history = [ ] ):
    clear_terminal ( )
    display_game_banner ( )
    display_guess_history ( len ( secret ), history )
    show_colorized_keyboard ( guesses )


def display_secret_word_definition ( secret ):
    print ( "Your secret word was ", secret, "!", sep = "" )

    wordnet_data = wordnet.synsets ( secret )
    if not wordnet_data:
        print ( "Uhoh. WordNet has nothing for", secret, "!", sep = "" )
    else:
        counter = 0
        for definition in wordnet_data:
            counter += 1
            print ( counter, ": ", definition.definition ( ), sep = "" )
            for example_sentence in definition.examples ( ):
                print ( '   "', example_sentence, '"', sep = "" )


def display_guess_history ( max_length, history = [ ] ):
    for colorized_guess in history:
        for colorized_letter in colorized_guess:
            print ( colorized_letter, end = " " )
        print ( )

    for i in range ( max_length - len ( history ) ):
        for x in range ( max_length ):
            print ( LETTER_PLACEHOLDER, end = " " )
        print ( )


def display_game_over_data ( secret, history ):
    show_current_game ( history )
    display_secret_word_definition ( secret )


################################################################
############################# MAIN #############################
################################################################

# TODO
#  can I use the wordnet lemma set only instead of using both sets?
wn_words = words.words ( )
wn_lemmas = set ( wordnet.all_lemma_names ( ) )

display_game_banner ( )

while True:

    scored_guesses = [ ]
    colorized_history = [ ]
    user_guess = ""
    game_secret = pick_secret_word ( wn_words, wn_lemmas, scored_guesses )
    show_current_game ( game_secret )

    while not is_game_over ( game_secret, user_guess, len ( scored_guesses ) ):
        user_guess = ask_user_for_guess ( game_secret, wn_words, wn_lemmas )
        scored_guesses.append ( score_one_guess ( game_secret, user_guess ) )
        show_current_game ( game_secret, scored_guesses, colorized_history )

    display_game_over_data ( game_secret, colorized_history )

    if user_wants_to_continue ( ):
        show_current_game ( )
    else:
        finish ( )

################################################################
################################################################
################################################################
