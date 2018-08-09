import random
from flask import Flask, render_template, request
app = Flask(__name__)
import jinja2

@app.route('/', methods = ['POST', 'GET'])
def index():
    keyword = "John Cage"
    if request.method == 'POST':
        keyword = request.form['keyword']
    text = open('text.txt', 'r').read()
    if request.method == 'POST':
        user_entered_text = request.form['text']
        if (len(user_entered_text) > 1000):
            text = user_entered_text

    wingSparsity = 10 # How many words do we want in the "wings" on either side of the keyword spine?

    def match_letters(letter1, letter2):
        if (((letter1.upper() == letter2) or (letter1.lower() == letter2)) and (letter1.isalpha())):
            return True
        else:
            return False

    for char in '0123456789.,;:?/|\\\'\"-!%^&*()[]{}<>_=+~`@#$%¡¿«»–—‘’“”':
        text = text.replace(char, "")

    for char in '0123456789.,;:?/|\\\'\"-!%^&*()[]{}<>_= +~`@#$%¡¿«»–—‘’“”':
        keyword = keyword.replace(char, "")


    i = 0 # keyword index
    j = 0 # text index
    lines = []
    keyLetterDistance = [0]         # we start index 0, the first letter in the text
    while i < len(keyword):         # loop through the keyword

        while j < len(text):        # loop through the text

            if match_letters(keyword[i], text[j]):        # do they match?

                lines.append([text[0 : j], text[j : -1]]) # slice the whole text just before that point

                keyLetterDistance.append(j)               # create a list of the slice-point indices

                i += 1
                j += 1
                break

            else:
                j += 1

    keyLetterDistance.append(len(text))

    poem = []
    for index, line in enumerate(lines):

        # Split right and left wings into word-indexed lists
        left = line[0].split(' ')
        right = line[1].split(' ')

        # intersection of right
        left = list(filter(None, left))  # filter out empty lists
        right = list(filter(None, right))

        poem.append([left[-1:], right[0:1], right[0:-1]])


    # change all the right wings
    for index, sublist in enumerate(poem):
        # The last time is different because we don't want all the rest of the text
        if (index == len(poem)-1):
            poem[index][2] = right[1:random.randint(1, wingSparsity)]
        else:
            currentLineLength = len(poem[index][2])
            nextLineLength    = len(poem[index+1][2])
            rightWingRange = abs(currentLineLength - nextLineLength) # this is the largest possible right line length
            rightWingList = poem[index][2]
            poem[index][2] = rightWingList[1 : rightWingRange]


    # Create the left wing for the first line
    for index, sublist in enumerate(poem):
        if (index == 0):
            preText = text[0:keyLetterDistance[1]]
            preText = preText.split(' ')

            # If the starting wing text would be too long, we limit it
            if len(preText) > wingSparsity:
                preText = preText[random.randint(len(preText)-wingSparsity, len(preText)-2):-2] # Use -2 because we don't want
                                                                                         # to include the keyword
                                                                                         # letter on the left side
            else:
                preText = preText[0:-1]

            poem[0].insert(0, preText)
        elif (len(sublist) < 4):
            poem[index].insert(0, [])  # we add empty lists
        else:
            raise ValueError('A sublist with four or more indices was already found in "poem"')

    # Look for any cases where the right-most wing word is the same as the left part of the spine
    # In any such cases, drop the right-most wing word
    for index, sublist in enumerate(poem):
        if index < len(poem)-1:                                     # This gets a bit messy, but we just need to access
            if ((poem[index][3][-1:]) == (poem[index+1][1][-1:])):  # the last value in the fourth sub-sublist in each line
                del poem[index][3][-1:]

    # correct for the case in which the keyword letter is the first letter in a word (would not have a space before it)
    for index, hitPoint in enumerate(keyLetterDistance[1:-1]):
        if (text[hitPoint-1] == " "):    # check if the character right before the keyword letter is a space
            poem[index][1].append(" ")   # if it is then insert a space in the right spot

    # Here we take the right-hand wing text and split it so that some of it can go into the left-hand side
    for index, sublist in enumerate(poem):
        if (len(poem[index][3]) > wingSparsity):
            poem[index][3] = [ poem[index][3][i] for i in sorted(random.sample(range(len(poem[index][3])), wingSparsity)) ]

        if (len(poem[index][3]) > 1):
            wingLength = random.randint(0, (len(poem[index][3])-1))
            wingText = poem[index][3]
            rightWing = wingText[0 : wingLength]
            leftWing = wingText[wingLength : (len(poem[index][3]))]
            if index < len(poem)-1:
                poem[index][3] = rightWing
                poem[index+1][0] = leftWing

    # Convert the doubly-nested list to a list of string doubles (each sublist reprosenting one line of the poem)
    for index, sublist in enumerate(poem):
        leftSide1 = " ".join(poem[index][0])
        leftSide2 = " ".join(poem[index][1])
        leftSide = f"{leftSide1} {leftSide2}"

        if leftSide[0].isspace():     # In the case of an empty list, a space would be added, so we take that out
            leftSide = leftSide[1:]

        rightSide1 = " ".join(poem[index][2])
        rightSide2 = " ".join(poem[index][3])
        rightSide = f"{rightSide1} {rightSide2}"

        if rightSide[-1].isspace():   # Again we take out an ending space if it exists
            rightSide = rightSide[0:-1]

        poem[index] = [leftSide, rightSide]

    poem_list = [item for sublist in poem for item in sublist]
    return render_template('index.html', poem = poem_list)

if __name__ == '__main__':
    app.run(debug = True, port=33507)
