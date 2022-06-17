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


LETTER_PLACEHOLDER = "☐"  # "*"

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


def colorize_one_guess ( scored_guess ):
    guess, score = scored_guess
    colorized_guess = [ ]
    for i in range ( len ( guess ) ):
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

    return colorized_guess


# TODO
#  use formatted string or padding methods
def display_colorized_keyboard ( guesses ):
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

    print ( )
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
                    print ( ' ', end='' )
            print ( letter, end=' ' )
        print ( )
    print ( )


# select a random five letter secret
# take it down to lower case, even though likely the NLTK data set is already lower case
def draw_secret_word ( words, lemmas, guesses ):
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
        print ( "Secret word and user guess are different length. Exit." )
        quit ( )

    secret_letters_occurrences = { }
    for i in range ( len ( secret_word ) ):
        if secret_word [ i ] not in secret_letters_occurrences:
            secret_letters_occurrences [ secret_word [ i ] ] = 1
        else:
            secret_letters_occurrences [ secret_word [ i ] ] = secret_letters_occurrences [ secret_word [ i ] ] + 1

    scored_guess = [ guess_word ]
    user_guess_score = [ ]
    for i in range ( len ( secret_word ) ):
        if secret_word [ i ] == guess_word [ i ] and secret_letters_occurrences [ secret_word [ i ] ] > 0:
            user_guess_score.insert ( i, Score.HIT )
            secret_letters_occurrences [ secret_word [ i ] ] = secret_letters_occurrences [ secret_word [ i ] ] - 1
        elif guess_word [ i ] in secret_word and secret_letters_occurrences [ secret_word [ i ] ] > 0:
            user_guess_score.insert ( i, Score.MISS )
            secret_letters_occurrences [ secret_word [ i ] ] = secret_letters_occurrences [ secret_word [ i ] ] - 1
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
    while len ( guess_word ) != len (
            secret ) or guess_word not in words or guess_word.istitle ( ) or guess_word not in lemmas:
        guess_word = input ( "Your guess: " ).lower ( )

    return guess_word


def user_wants_to_continue ():
    continue_game = input ( "Play again? (y)/n: " )
    return continue_game in [ "", "Y", "y" ]


def display_game_over_data ():
    print ( )
    if user_score > robot_score:
        print ( "You WON!" )
    elif user_score == robot_score:
        print ( "Game is a TIE." )
    else:
        print ( "Sorry, you LOST." )

    print ( "Game score", user_score, ":", robot_score )
    print ( "Play again soon!" )

    quit ( )


def display_game_banner ():
    print ( "---------------------------------------" )
    print ( "|                                     |" )
    print ( "|       WELCOME TO OPEN WORDLE!       |" )
    print ( "|                                     |" )
    print ( "---------------------------------------" )


def display_current_game ( secret, guesses, history ):
    clear_terminal ( )
    display_game_banner ( )
    display_guess_history ( len ( secret ), history )
    display_colorized_keyboard ( guesses )


def display_guess_history ( max_length, history ):
    for colorized_guess in history:
        for colorized_letter in colorized_guess:
            print ( colorized_letter, end=" " )
        print ( )

    for i in range ( max_length - len ( history ) ):
        for x in range ( max_length ):
            print ( LETTER_PLACEHOLDER, end=" " )
        print ( )


# TODO
#  use formatted string or string padding methods
def display_current_turn_end ( secret ):
    print ( "The secret word is ", secret, "!", sep="" )
    wordnet_data = wordnet.synsets ( secret )
    counter = 1
    for definition in wordnet_data:
        print ( counter, ": ", definition.definition ( ), sep="" )
        for example_sentence in definition.examples ( ):
            print ( '   "', example_sentence, '"', sep="" )
        counter += 1


################################################################
############################# MAIN #############################
################################################################

# TODO
#  prepare words lookup instead of using words and lemma sets
wn_words = words.words ( )
wn_lemmas = set ( wordnet.all_lemma_names ( ) )

display_game_banner ( )

while True:

    scored_guesses = [ ]
    colorized_history = [ ]
    user_guess = ""
    game_secret = draw_secret_word ( wn_words, wn_lemmas, scored_guesses )

    while not is_game_over ( game_secret, user_guess, len ( scored_guesses ) ):
        display_current_game ( game_secret, scored_guesses, colorized_history )
        user_guess = ask_user_for_guess ( game_secret, wn_words, wn_lemmas )
        current_guess_scored = score_one_guess ( game_secret, user_guess )
        scored_guesses.append ( current_guess_scored )
        colorized_history.append ( colorize_one_guess ( current_guess_scored ) )

    display_current_game ( game_secret, scored_guesses, colorized_history )
    display_current_turn_end ( game_secret )

    if not user_wants_to_continue ( ):
        display_current_game ( game_secret, scored_guesses, colorized_history )
        display_current_turn_end ( game_secret )
        display_game_over_data ( )
