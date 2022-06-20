# OPEN WORDLE without a daily limit
#
# TODOs
#    thread the abysmally slow wordnet lookup, display a UI indicator
#    thread secret word drawing with UI progress indicator
#    Popup window UI


from nltk.corpus import words
from nltk.corpus import wordnet
from os import system, name
import random

# The longest dictionary word according to Wikipedia:
# "Pneumonoultramicroscopicsilicovolcanoconiosis"
# 45 letters - the disease silicosis
class GameMode:
    EASY        = [  4,  5 ]
    NORMAL      = [  5, 10 ]
    ADVANCED    = [ 10, 15 ]
    EXPERT      = [ 15, 20 ]
    INSANE      = [ 20, 50 ]

class Colorize:
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    END     = '\033[0m'


class Score:
    HIT     = 2
    MISS    = 1
    FAIL    = 0


LETTER_PLACEHOLDER = "☐"

KEYBOARD = [ [ 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p' ],
             [ 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ],
             [ 'z', 'x', 'c', 'v', 'b', 'n', 'm' ] ]

# game score across all turns
global user_score
user_score = 0
global robot_score
robot_score = 0


def ask_for_hardness_level ():
    print ( "We measure game level by secret word length." )
    print ( "1. easy:     up to 5 letters." )
    print ( "2. normal:    5 to 10 letters" )
    print ( "3. advanced: 10 to 15 letters." )
    print ( "4. expert:   15 to 20 letters." )
    print ( "5. insane:   20 letters and above." )

    expected_modes = [ "easy", "normal", "advanced", "expert", "insane", "1", "2", "3", "4", "5", "" ]
    input_prompt = create_input_prompt ( expected_modes )
    user_mode = input ( input_prompt ).lower ( )
    while user_mode not in expected_modes:
        user_mode = input ( "1 - 5: (2) " ).lower ( )

    if "" == user_mode:
        return GameMode.NORMAL
    elif "easy" == user_mode or "1" == user_mode:
        return GameMode.EASY
    elif "normal" == user_mode or "2" == user_mode:
        return GameMode.NORMAL
    elif "advanced" == user_mode or "3" == user_mode:
        return GameMode.ADVANCED
    elif "expert" == user_mode or "4" == user_mode:
        return GameMode.EXPERT
    elif "insane" == user_mode or "5" == user_mode:
        return GameMode.EXPERT

    return user_mode


def create_input_prompt ( options ):
    prefix = "Please indicate "
    delimiter = '/'
    prompt = delimiter.join ( filter ( lambda x: len ( x ) > 1, options) )
    preselected = ": (" + options [ 1 ] + ") "

    return prefix + prompt + preselected


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
def draw_secret_word ( game_mode, words, guesses ):
    secret_word = ""
    while invalid_random_word ( secret_word, guesses, game_mode ):
        secret_word = random.choice ( words )

    return secret_word.lower ( )


def invalid_random_word ( secret_word, guesses, game_mode ):
    lower_limit, upper_limit = game_mode
    return 0 == len ( secret_word ) \
           or len ( secret_word ) > upper_limit \
           or len ( secret_word ) < lower_limit \
           or secret_word in guesses \
           or secret_word.istitle ( )


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


def is_game_over ( secret, guess, tries ):
    if secret == guess:
        global user_score
        user_score += 1
    elif len ( secret ) == tries:
        global robot_score
        robot_score += 1
    return secret == guess or len ( secret ) == tries


def ask_user_for_guess ( secret, wordlist ):
    user_prompt = "Your guess: "
    valid = False
    while not valid:
        guess_word = input ( user_prompt ).lower ( )
        if guess_word not in wordlist:
            user_prompt = "Try a valid word: "
        elif guess_word.istitle ( ):
            user_prompt = "No names or titles: "
        elif 0 == len ( guess_word ):
            user_prompt = "Cannot be empty: "
        elif len ( guess_word ) != len ( secret ):
            user_prompt = "Try " + str ( len ( secret ) ) + " letters: "
        else:
            valid = True

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
display_game_banner ( )

game_mode = ask_for_hardness_level ( )
while True:
    scored_guesses = [ ]
    colorized_history = [ ]
    user_guess = ""
    game_secret = draw_secret_word ( game_mode, wn_words, scored_guesses )

    while not is_game_over ( game_secret, user_guess, len ( scored_guesses ) ):
        display_current_game ( game_secret, scored_guesses, colorized_history )
        user_guess = ask_user_for_guess ( game_secret, wn_words )
        current_guess_scored = score_one_guess ( game_secret, user_guess )
        scored_guesses.append ( current_guess_scored )
        colorized_history.append ( colorize_one_guess ( current_guess_scored ) )

    display_current_game ( game_secret, scored_guesses, colorized_history )
    display_current_turn_end ( game_secret )

    if not user_wants_to_continue ( ):
        display_current_game ( game_secret, scored_guesses, colorized_history )
        display_current_turn_end ( game_secret )
        display_game_over_data ( )
