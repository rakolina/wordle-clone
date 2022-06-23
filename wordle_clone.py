# OPEN WORDLE without a daily limit
#
# TODOs
#    thread the abysmally slow wordnet lookup, display a UI indicator
#    thread secret word drawing with UI progress indicator
#    Popup window UI


from nltk.corpus import stopwords, \
    words, \
    wordnet
from os import system, \
    name
import random
import GameMode, \
    Colorize, \
    GameScore, \
    GameConstants

# game score across all turns
global user_score
user_score = 0
global robot_score
robot_score = 0


def ask_for_hardness_level ():
    clear_terminal ( )
    print ( "Choose secret word length:" )
    count = 1
    expected_modes = [ "" ]  ## allow hitting enter to cnfirm preselected hardness level
    for label, left, right in GameMode.game_modes:
        expected_modes.append ( label )
        expected_modes.append ( str ( count ) )
        print ( str ( count ) + ". " + label + " mode: between " + str ( left ) + " and " + str ( right ) + " letters." )
        count += 1

    # input_prompt = create_input_prompt ( expected_modes )
    preselected = "Your choice: (" + expected_modes [ 1 ] + ") "
    user_mode = input ( preselected ).lower ( )
    while user_mode not in expected_modes:
        user_mode = input ( "1 - 5: (1) " ).lower ( )

    if "" == user_mode or "casual" == user_mode or "1" == user_mode:
        return GameMode.game_modes [ 0 ]
    elif "normal" == user_mode or "2" == user_mode:
        return GameMode.game_modes [ 1 ]
    elif "advanced" == user_mode or "3" == user_mode:
        return GameMode.game_modes [ 2 ]
    elif "expert" == user_mode or "4" == user_mode:
        return GameMode.game_modes [ 3 ]
    elif "insane" == user_mode or "5" == user_mode:
        return GameMode.game_modes [ 4 ]

    return user_mode


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
        if GameScore.HIT == score [ i ]:
            colorized_letter = Colorize.GREEN + guess [ i ] + Colorize.END
        elif GameScore.MISS == score [ i ]:
            colorized_letter = Colorize.YELLOW + guess [ i ] + Colorize.END
        elif GameScore.FAIL == score [ i ]:
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
    for keyboard_row in GameConstants.KEYBOARD:
        colorized_keyboard_row = [ ]
        for keyboard_letter in keyboard_row:
            if keyboard_letter not in total_letter_scores.keys ( ):
                colorized_keyboard_row.append ( keyboard_letter )
            elif total_letter_scores [ keyboard_letter ] == GameScore.HIT:
                colorized_keyboard_row.append ( Colorize.GREEN + keyboard_letter + Colorize.END )
            elif total_letter_scores [ keyboard_letter ] == GameScore.MISS:
                colorized_keyboard_row.append ( Colorize.YELLOW + keyboard_letter + Colorize.END )
            elif total_letter_scores [ keyboard_letter ] == GameScore.FAIL:
                colorized_keyboard_row.append ( Colorize.RED + keyboard_letter + Colorize.END )

        display_offset = False
        for letter in colorized_keyboard_row:
            if 10 > len ( colorized_keyboard_row ) and not display_offset:
                display_offset = True
                for i in range ( 10 - len ( colorized_keyboard_row ) ):
                    print ( ' ', end = '' )
            print ( letter, end = ' ' )
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
    label, lower_limit, upper_limit = game_mode
    return 0 == len ( secret_word ) \
           or len ( secret_word ) > upper_limit \
           or len ( secret_word ) < lower_limit \
           or secret_word in guesses


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
            user_guess_score.insert ( i, GameScore.HIT )
            secret_letters_occurrences [ secret_word [ i ] ] = secret_letters_occurrences [ secret_word [ i ] ] - 1
        elif guess_word [ i ] in secret_word and secret_letters_occurrences [ secret_word [ i ] ] > 0:
            user_guess_score.insert ( i, GameScore.MISS )
            secret_letters_occurrences [ secret_word [ i ] ] = secret_letters_occurrences [ secret_word [ i ] ] - 1
        else:
            user_guess_score.insert ( i, GameScore.FAIL )

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


def display_game_banner ( mode ):
    banner_width = 40
    frame = "".join ( [ GameConstants.LETTER_PLACEHOLDER for i in range ( banner_width ) ] )
    welcome = "WELCOME TO OPEN WORDLE!"
    label, left, right = mode
    game_mode_label = "MODE: " + label.upper() + " (" + str ( left ) + " - " + str ( right ) + " letters)"

    print ( frame )
    print ( GameConstants.LETTER_PLACEHOLDER, welcome.center ( banner_width - 2 ), GameConstants.LETTER_PLACEHOLDER, sep="" )
    print ( GameConstants.LETTER_PLACEHOLDER, game_mode_label.center ( banner_width - 2 ), GameConstants.LETTER_PLACEHOLDER, sep="" )
    print ( frame )
    print ( )


def display_updated_game ( secret, guesses, history, mode ):
    clear_terminal ( )
    display_game_banner ( mode )
    display_guess_history ( len ( secret ), history )
    display_colorized_keyboard ( guesses )


def display_guess_history ( max_length, history ):
    for colorized_guess in history:
        for colorized_letter in colorized_guess:
            print ( colorized_letter, end = " " )
        print ( )

    for i in range ( max_length - len ( history ) ):
        for x in range ( max_length ):
            print ( GameConstants.LETTER_PLACEHOLDER, end = " " )
        print ( )


# TODO
#  use formatted string or string padding methods
# from itertools import chain
# from nltk.corpus import wordnet
#
# synonyms = wordnet.synsets(text)
# lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
def display_current_turn_end ( secret ):
    print ( "The secret word is ", secret, "!", sep = "" )
    wn_synonyms = wordnet.synsets ( secret )
    counter = 1
    for syn in wn_synonyms:
        print ( counter, ": ", syn.definition ( ), sep = "" )
        for example_sentence in syn.examples ( ):
            print ( '   "', example_sentence, '"', sep = "" )
        counter += 1


# get a set of words
# prune stopwords
# prune titles
# prune very short words
# prune out words not defined in nltk
# TODO
#    use better word definiton lookup
def prepare_secret_word_lookup ():
    game_lookup = []
    game_stopwords = stopwords.words ( GameConstants.EN )
    wn_lemmas = set ( wordnet.all_lemma_names ( ) )
    wn_words = words.words ( )
    for word in wn_words:
        if acceptable ( game_stopwords, wn_lemmas, word ):
            game_lookup.append ( word )
    return game_lookup


def acceptable ( game_stopwords, wn_lemmas, word ):
    return word in wn_lemmas \
           and not word.istitle ( ) \
           and word not in game_stopwords \
           and GameConstants.MINIMUM_LENGTH < len ( word )


#############################################################################################
# MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #
#############################################################################################


# TODO
#  prepare words lookup instead of using words and lemma sets
game_wordset = prepare_secret_word_lookup ( )
game_mode = ask_for_hardness_level ( )
while True:
    scored_guesses = [ ]
    colorized_history = [ ]
    user_guess = ""
    game_secret = draw_secret_word ( game_mode, game_wordset, scored_guesses )

    while not is_game_over ( game_secret, user_guess, len ( scored_guesses ) ):
        display_updated_game ( game_secret, scored_guesses, colorized_history, game_mode )
        user_guess = ask_user_for_guess ( game_secret, game_wordset )
        current_guess_scored = score_one_guess ( game_secret, user_guess )
        scored_guesses.append ( current_guess_scored )
        colorized_history.append ( colorize_one_guess ( current_guess_scored ) )

    display_updated_game ( game_secret, scored_guesses, colorized_history, game_mode )
    display_current_turn_end ( game_secret )

    if not user_wants_to_continue ( ):
        display_updated_game ( game_secret, scored_guesses, colorized_history, game_mode )
        display_current_turn_end ( game_secret )
        display_game_over_data ( )
