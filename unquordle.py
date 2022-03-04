from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import json
import time
import keyboard

# Initialize Selenium
ser = Service("C:\\Program Files (x86)\chromedriver.exe")
op = webdriver.ChromeOptions()
browser = webdriver.Chrome(service=ser, options=op)

# Load JSON file with possible guesses and solutions
f = json.load(open('words.json'))

# Enter guess
def enter_guess(word):
    keyboard.write(word, delay=0.05)
    keyboard.press_and_release('enter')

# Evaluate guess
def evaluate_guess(game_board, guess_number):
    evaluation = []
    row = game_board.find_elements(By.XPATH, "./*")[guess_number]
    tiles = row.find_elements(By.XPATH, "./*")
    for tile in tiles:
        if "incorrect" in tile.get_attribute("aria-label"):
            evaluation.append(0)
        elif "different spot" in tile.get_attribute("aria-label"):
            evaluation.append(1)
        else:
            evaluation.append(2)
    return evaluation

# Trim down potential solutions
def trim_list_of_guesses(words, selected_word, evaluation):
    for i in range(5):
        if evaluation[i] == 0:
            remove = True
            occurrences = find(selected_word, selected_word[i])
            occurrences.remove(i)
            if len(occurrences) > 0:
                for occurrence in occurrences:
                    if evaluation[occurrence] == 1 or evaluation[occurrence] == 2:
                        remove = False
            if remove:
                for word in list(words):
                    if selected_word[i] in word:
                        words.remove(word)
        elif evaluation[i] == 1:
            for word in list(words):
                if selected_word[i] not in word or selected_word[i] == word[i]:
                    words.remove(word)
        else:
            for word in list(words):
                if selected_word[i] != word[i]:
                    words.remove(word)
    return words

# Return list of occurrences of a character in a string
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

# Select next word
def select_word(words):
    unique = True
    tmp = []
    for word in words:
        for i in range(len(word)):
            for j in range(i + 1, len(word)):
                if word[i] == word[j]:
                    unique = False
        if unique:
            tmp.append(word)
        unique = True
    if len(tmp) > 0:
        return tmp[0]
    else:
        return words[0]

# Solve Quordle
def unquordle():
    # Set up Selenium browser
    browser.get("https://www.quordle.com")

    # Start program when escape key is pressed
    keyboard.wait('esc')

    # Initialize potential solutions
    trimmed_down_lists = [f['solutions'], f['solutions'], f['solutions'], f['solutions']]

    # Initialize first guess
    # https://www.youtube.com/watch?v=fRed0Xmc2Wg
    selected_word = "crate"

    # Initialize list with incomplete boards
    incomplete_boards = [0, 1, 2, 3]

    # Initialize counters
    guess_number = 0

    # Iterate for nine attempts
    while guess_number < 9:

        # Enter guess
        enter_guess(selected_word)

        # Evaluate guess
        for incomplete_board in list(incomplete_boards):

            # Retrieve game board
            board_path = "//div[@aria-label='Game Board " + str(incomplete_board + 1) + "']"
            game_board = browser.find_element(By.XPATH, board_path)
            evaluation = evaluate_guess(game_board, guess_number)

            if sum(evaluation) == 10:
                incomplete_boards.remove(incomplete_board)
            else:
                # Trim down potential solutions
                trimmed_down_lists[incomplete_board] = trim_list_of_guesses(list(trimmed_down_lists[incomplete_board]), selected_word, evaluation)

        # Check if Quordle has been solved
        if len(incomplete_boards) == 0:
            print("Solved in {} attempts!".format(guess_number + 1))
            return

        # Select next guess
        selected_word = select_word(trimmed_down_lists[incomplete_boards[0]])

        # Wait for site to reveal result of previous guess
        time.sleep(0.5)

        # Increment guess number
        guess_number = guess_number + 1

    # Admit failure
    if guess_number == 8:
        print("Could not guess in nine attempts!")

if __name__ == '__main__':
    unquordle()