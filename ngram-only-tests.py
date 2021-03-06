'''

This module is for tests using only n-grams (i.e. not also including any other features).

If other features are to be tested in addition to n-grams, use ngram-and-non-ngram-tests-combined.py.

If n-grams are NOT being employed, use non-ngram-only-tests.py.

The code relating to scikit-learn was adapted from code on the scikit-learn website: https://scikit-learn.org/

'''
import numpy as np
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer

corpus = []  # List of sentences in human-readable form (i.e. not in a bag of words representation).
documentClassifications = []  # Formal or informal? true = formal, false = informal.
formalityScoreList = []  # Mechanical Turk formality scores.
nonDocumentData = []  # List of lists, each containing a sentence's attribute data.
dataFileFieldNames = []  # The field names from the top of the data spreadsheet.
corpus = []  # List of sentences in human-readable form (i.e. not in a bag of words representation).
documentClassifications = []  # Stored as strings - true = formal, false = informal.
formalityScoreList = []  # Mechanical Turk formality scores.
nonDocumentData = []  # List of lists, each containing a sentence's attribute data.
dataFileFieldNames = []  # The field names from the top of the data spreadsheet.
fileName = "new_formality_data.csv"


# Checks if the 'fileName' is the correct file name
def checkFileNameCorrect():
    global fileName
    print("The default data file name is ", fileName, "\n")
    print("If this is the name of the data file, press enter")
    newFileName = input("Otherwise, please provide the correct name, then press enter: ")
    if newFileName != "":
        fileName = newFileName
        print("\nThank you. The file name has been changed to", fileName)
    else:
        print("\nThank you. You have confirmed that the file name is correct:", fileName)


# Checks if file present. Code for this module adapted from:
# https://stackoverflow.com/questions/5627425/what-is-a-good-way-to-handle-exceptions-when-trying-to-read-a-file-in-python
def checkFilePresent():
    try:
        f = open(fileName, 'rb')
    except OSError:
        print("\nFile not found:", fileName)
        print("Please ensure that the data file is in the same folder as the program file and try again.")
        print("Exiting program.")
        sys.exit()


# This function loads the data from the file and stores it in global data structures.
def loadData():
    checkFileNameCorrect()  # Asks user is data file name is correct
    checkFilePresent()  # Checks if data file is present
    with open(fileName, encoding='utf-8') as inputFile:
        firstLine = inputFile.readline()
        firstLineAsList = firstLine.split(",")
        # Copy the data file field names into a global list:
        for items in firstLineAsList:
            dataFileFieldNames.append(items)

        # The sentence field is always the final field on the right. Therefore, the sentence index is the number of
        # fields up to and including the one immediately preceding the 'sentence' field.
        sentenceIndex = len(firstLineAsList) - 1
        for line in inputFile:

            # Searches through the line for commas, character by character. Stops when 'sentenceIndex' number of commas
            # have been encountered.
            # The document is located to the right of the comma corresponding to index 'sentenceIndex'.
            # Everything to the left of that comma is data relating to the document.
            numCommas = 0
            for character in range(len(line)):

                #  Increments numCommas whenever a comma is encountered in the line.
                if line[character] == ",":
                    numCommas = numCommas + 1

                #  The code below is run when when the number of commas encountered equals the value of 'sentenceIndex'.
                #  When the code below is run, it means that everything on the line to the right of the last comma
                #  encountered is part of the sentence, and not attribute data.
                if numCommas == sentenceIndex:
                    dataExcludingSentence = line[:character]
                    dataExcludingSentenceAsList = dataExcludingSentence.split(",")
                    nonDocumentData.append(dataExcludingSentenceAsList)
                    formalityScore = float(dataExcludingSentenceAsList[2])
                    formalityScoreList.append(formalityScore)

                    # If mechanical Turk formality score >=4 then formal status = true:
                    documentClassifications.append(formalityScore >= 4)
                    documentToAdd = line[character + 1:]  # The rest of the current line is comprised of the document
                    documentToAdd.replace('\n', '')  # Removes 'next line' symbol \n from the end of the document

                    # Puts document into a list of Strings:
                    corpus.append(documentToAdd)
                    break  # returns to the outer 'for' loop, so the next line can be processed.
    inputFile.close()
    print("\nNo of records uploaded: ", len(corpus))


# This function performs the machine learning test and outputs a classification prediction result summary.
def classificationResults(featureData, classificationLabels, featureDescription):
    #  The two lines below convert the lists passed into the function to arrays.
    X = np.array(featureData)
    y = np.array(classificationLabels)

    #  Splits the data into training and testing sets using 5 split k fold:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=12345)
    skf.split(X, y)
    X_train = []
    X_test = []
    y_train = []
    y_test = []
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

    # Fits the data to a model. The model is initially instantiated as SVC so that the definitions of 'classifier' in
    # the 'if' statements below it aren't out of scope of the rest of the module.
    model = SVC(gamma='scale', kernel='linear', probability=True).fit(X_train, y_train)
    if classifier == "Logistic Regression":
        model = LogisticRegression(random_state=0, solver='lbfgs', max_iter=1000).fit(X_train, y_train)
    if classifier == "Multinomial Bayes":
        model = MultinomialNB().fit(X_train, y_train)
    if classifier == "Random Forest":
        model = RandomForestClassifier().fit(X_train, y_train)

    # Generates a prediction for each sentence, and stores them in a list called 'predictions'.
    predictions = model.predict(np.array(X_test))

    # Calculates true positives, true negatives, false positives and false negatives:
    truePositives = 0
    trueNegatives = 0
    falsePositives = 0
    falseNegatives = 0
    numberInList = 0
    for prediction in predictions:
        # Is this a formal sentence which was predicted to be formal?
        if y_test[numberInList] and prediction:
            truePositives = truePositives + 1

        # Is this an informal sentence which was predicted to be informal?
        if not y_test[numberInList] and not prediction:
            trueNegatives = trueNegatives + 1

        # Is this an informal sentence which was predicted to be formal?
        if not y_test[numberInList] and prediction:
            falsePositives = falsePositives + 1

        # Is this a formal sentence which was predicted to be informal?
        if y_test[numberInList] and not prediction:
            falseNegatives = falseNegatives + 1
        numberInList = numberInList + 1

    # Performance metrics
    if (truePositives + trueNegatives + falsePositives + falseNegatives) > 0:
        accuracy = (truePositives + trueNegatives) / (truePositives + trueNegatives + falsePositives + falseNegatives)
    else:
        accuracy = 0
    if (truePositives + falsePositives) > 0:
        precision = truePositives / (truePositives + falsePositives)
    else:
        precision = 0
    if (truePositives + falseNegatives) > 0:
        recall = truePositives / (truePositives + falseNegatives)
    else:
        recall = 0
    if (trueNegatives + falsePositives) > 0:
        fallout = falsePositives / (trueNegatives + falsePositives)  # 'Fallout' is the same as the false positive rate.
    else:
        fallout = 0
    balAccuracy = balanced_accuracy_score(y_test, predictions)

    # Area under roc curve
    y_scores = model.predict_proba(X_test)
    y_scores = y_scores[:, 1]
    rocAreaUnderCurve = roc_auc_score(y_test, y_scores)

    # Console output
    print("\nRESULTS SUMMARY\n" + "---------------")
    print("\nFeature tested: ", featureDescription)
    print("Classifier: " + classifier, "\n")
    print("Total predictions: ", numberInList)
    print("TRUE POSITIVES: ", truePositives)
    print("FALSE POSITIVES: ", falsePositives)
    print("TRUE NEGATIVES: ", trueNegatives)
    print("FALSE NEGATIVES: ", falseNegatives)

    # Division by zero is illegal, so if the denominator is zero, then 'N/A' is given as the metric's value.
    if accuracy > 0:
        print("Accuracy: %3.2f" % accuracy)
    else:
        print("Accuracy: N/A")
    if precision > 0:
        print("Precision: %3.2f" % precision)
    else:
        print("Precision: N/A")
    if recall > 0:
        print("Recall: %3.2f" % recall)
    else:
        print("Recall: N/A")
    if fallout > 0:
        print("False positive rate: %3.2f" % fallout)
    else:
        print("False positive rate: N/A")
    print("AUC: %3.2f" % rocAreaUnderCurve)
    print("Balanced accuracy: %3.2f" % balAccuracy)


# Asks the user what type of n-gram they want to test.
def askForType():
    print("\nThe n-gram types are: ")
    print("1 - Unigram")
    print("2 - Bigram")
    print("3 - Trigram")
    print("4 - Unigram and bigram combined")
    print("5 - Unigram, bigram and trigram combined")
    userChoice = input("\nChoose an option by typing a number between 1 and 5 and then press 'enter': ")
    if userChoice.isnumeric():
        global nGramType
        userChoice = int(userChoice)
        if userChoice == 1:
            nGramType = "unigram"
            return
        if userChoice == 2:
            nGramType = "bigram"
            return
        if userChoice == 3:
            nGramType = "trigram"
            return
        if userChoice == 4:
            nGramType = "1, 2 gram"
            return
        if userChoice == 5:
            nGramType = "1, 2, 3 gram"
            return
        else:
            print("\nInvalid selection. Please try again")
            askForType()
    # If non-numeric value entered:
    else:
        print("\nInvalid selection. Please try again")
        askForType()


# Asks user whether n-gram will be binary, non-binary or TF-IDF representation
def askForRepresentation():
    print("\nThe representation options are: ")
    print("1 - Binary")
    print("2 - Non-Binary")
    print("3 - TF-IDF")
    userChoice = input("\nChoose an option by typing a number between 1 and 3 and then press 'enter': ")
    if userChoice.isnumeric():
        global representation
        userChoice = int(userChoice)
        if userChoice == 1:
            representation = "binary"
            return
        if userChoice == 2:
            representation = "non-binary"
            return
        if userChoice == 3:
            representation = "TF-IDF"
            return
        else:
            print("\nInvalid selection. Please try again")
            askForRepresentation()

    # If non-numeric value entered:
    else:
        print("\nInvalid selection. Please try again")
        askForRepresentation()


# Asks the user if they want stop words including in their test
def askAboutStopWords():
    print("\nThe stop word options are: ")
    print("1 - Include stop words")
    print("2 - No, do not include stop words")
    userChoice = input("\nChoose an option by typing either 1 or 2 and then press 'enter': ")
    if userChoice.isnumeric():
        global stops
        userChoice = int(userChoice)
        if userChoice == 1:
            stops = "with stop words"
            return
        if userChoice == 2:
            stops = "without stop words"
            return
        else:
            print("\nInvalid selection. Please try again")
            askAboutStopWords()

    # If non-numeric value entered:
    else:
        print("\nInvalid selection. Please try again")
        askAboutStopWords()


# Asks the user which classifier they want
def askForClassifier():
    print("\nThe classifiers are: \n1 - Support Vector Machine\n2 - Logistic Regression\n3 - Multinomial Bayes\n"
          "4 - Random Forest")
    classifierChoice = input("\nPlease choose a classifier by typing a number between 1 and 4 and then press 'enter': ")
    if classifierChoice.isnumeric():
        classifierChoice = int(classifierChoice)
        global classifier
        if classifierChoice == 1:
            print("You have selected Support Vector Machine")
            classifier = "Support Vector Machine"
            return
        if classifierChoice == 2:
            print("You have selected Logistic Regression")
            classifier = "Logistic Regression"
            return
        if classifierChoice == 3:
            print("You have selected Multinomial Bayes")
            classifier = "Multinomial Bayes"
            return
        if classifierChoice == 4:
            print("You have selected Random Forest")
            classifier = "Random Forest"
            return
        else:
            print("\nThat was not a valid selection. Please try again.")
            askForClassifier()
    else:
        print("\nThat was not a valid selection. Please try again.")
        askForClassifier()


# Selects the correct vector type to create based on the user's test choices.
def setVector(nGramType, representation, stops):
    # UNIGRAMS

    # Unigram, binary representation, stop words included.
    if nGramType == "unigram" and representation == "binary" and stops == "with stop words":
        return CountVectorizer(binary=True, ngram_range=(1, 1))

    # Unigram, binary representation, stop words excluded.
    if nGramType == "unigram" and representation == "binary" and stops == "without stop words":
        return CountVectorizer(binary=True, stop_words='english', ngram_range=(1, 1))

    # Unigram, non-binary representation, stop words included.
    if nGramType == "unigram" and representation == "non-binary" and stops == "with stop words":
        return CountVectorizer(binary=False, ngram_range=(1, 1))

    # Unigram, non-binary representation, stop words excluded.
    if nGramType == "unigram" and representation == "non-binary" and stops == "without stop words":
        return CountVectorizer(binary=False, stop_words='english', ngram_range=(1, 1))

    # Unigram, TF-IDF representation, stop words included.
    if nGramType == "unigram" and representation == "TF-IDF" and stops == "with stop words":
        return TfidfVectorizer(ngram_range=(1, 1))

    # Unigram, TF-IDF representation, stop words excluded.
    if nGramType == "unigram" and representation == "TF-IDF" and stops == "without stop words":
        return TfidfVectorizer(stop_words='english', ngram_range=(1, 1))

    # BIGRAMS

    # Bigram, binary representation, stop words included.
    if nGramType == "bigram" and representation == "binary" and stops == "with stop words":
        return CountVectorizer(binary=True, ngram_range=(2, 2))

    # Bigram, binary representation, stop words excluded.
    if nGramType == "bigram" and representation == "binary" and stops == "without stop words":
        return CountVectorizer(binary=True, stop_words='english', ngram_range=(2, 2))

    # Bigram, non-binary representation, stop words included.
    if nGramType == "bigram" and representation == "non-binary" and stops == "with stop words":
        return CountVectorizer(binary=False, ngram_range=(2, 2))

    # Bigram, non-binary representation, stop words excluded.
    if nGramType == "bigram" and representation == "non-binary" and stops == "without stop words":
        return CountVectorizer(binary=False, stop_words='english', ngram_range=(2, 2))

    # Bigram, TF-IDF representation, stop words included.
    if nGramType == "bigram" and representation == "TF-IDF" and stops == "with stop words":
        return TfidfVectorizer(ngram_range=(2, 2))

    # Bigram, TF-IDF representation, stop words excluded.
    if nGramType == "bigram" and representation == "TF-IDF" and stops == "without stop words":
        return TfidfVectorizer(stop_words='english', ngram_range=(2, 2))

    # TRIGRAMS

    # Trigram, binary representation, stop words included.
    if nGramType == "trigram" and representation == "binary" and stops == "with stop words":
        return CountVectorizer(binary=True, ngram_range=(3, 3))

    # Trigram, binary representation, stop words excluded.
    if nGramType == "trigram" and representation == "binary" and stops == "without stop words":
        return CountVectorizer(binary=True, stop_words='english', ngram_range=(3, 3))

    # Trigram, non-binary representation, stop words included.
    if nGramType == "trigram" and representation == "non-binary" and stops == "with stop words":
        return CountVectorizer(binary=False, ngram_range=(3, 3))

    # Trigram, non-binary representation, stop words excluded.
    if nGramType == "trigram" and representation == "non-binary" and stops == "without stop words":
        return CountVectorizer(binary=False, stop_words='english', ngram_range=(3, 3))

    # Trigram, TF-IDF representation, stop words included.
    if nGramType == "trigram" and representation == "TF-IDF" and stops == "with stop words":
        return TfidfVectorizer(ngram_range=(3, 3))

    # Trigram, TF-IDF representation, stop words excluded.
    if nGramType == "trigram" and representation == "TF-IDF" and stops == "without stop words":
        return TfidfVectorizer(stop_words='english', ngram_range=(3, 3))

    # UNIGRAMS AND BIGRAMS COMBINED

    # Unigram and bigram combined, binary representation, stop words included.
    if nGramType == "1, 2 gram" and representation == "binary" and stops == "with stop words":
        return CountVectorizer(binary=True, ngram_range=(1, 2))

    # Unigram and bigram combined, binary representation, stop words excluded.
    if nGramType == "1, 2 gram" and representation == "binary" and stops == "without stop words":
        return CountVectorizer(binary=True, stop_words='english', ngram_range=(1, 2))

    # Unigram and bigram combined, non-binary representation, stop words included.
    if nGramType == "1, 2 gram" and representation == "non-binary" and stops == "with stop words":
        return CountVectorizer(binary=False, ngram_range=(1, 2))

    # Unigram and bigram combined, non-binary representation, stop words excluded.
    if nGramType == "1, 2 gram" and representation == "non-binary" and stops == "without stop words":
        return CountVectorizer(binary=False, stop_words='english', ngram_range=(1, 2))

    # Unigram and bigram combined, TF-IDF representation, stop words included.
    if nGramType == "1, 2 gram" and representation == "TF-IDF" and stops == "with stop words":
        return TfidfVectorizer(ngram_range=(1, 2))

    # Unigram and bigram combined, TF-IDF representation, stop words excluded.
    if nGramType == "1, 2 gram" and representation == "TF-IDF" and stops == "without stop words":
        return TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

    # UNIGRAMS, BIGRAMS AND TRIGRAMS COMBINED

    # Unigram, bigram and trigram combined, binary representation, stop words included.
    if nGramType == "1, 2, 3 gram" and representation == "binary" and stops == "with stop words":
        return CountVectorizer(binary=True, ngram_range=(1, 3))

    # Unigram, bigram and trigram combined, binary representation, stop words excluded.
    if nGramType == "1, 2, 3 gram" and representation == "binary" and stops == "without stop words":
        return CountVectorizer(binary=True, stop_words='english', ngram_range=(1, 3))

    # Unigram, bigram and trigram combined, non-binary representation, stop words included.
    if nGramType == "1, 2, 3 gram" and representation == "non-binary" and stops == "with stop words":
        return CountVectorizer(binary=False, ngram_range=(1, 3))

    # Unigram, bigram and trigram combined, non-binary representation, stop words excluded.
    if nGramType == "1, 2, 3 gram" and representation == "non-binary" and stops == "without stop words":
        return CountVectorizer(binary=False, stop_words='english', ngram_range=(1, 3))

    # Unigram, bigram and trigram combined, TF-IDF representation, stop words included.
    if nGramType == "1, 2, 3 gram" and representation == "TF-IDF" and stops == "with stop words":
        return TfidfVectorizer(ngram_range=(1, 3))

    # Unigram, bigram and trigram combined, TF-IDF representation, stop words excluded.
    if nGramType == "1, 2, 3 gram" and representation == "TF-IDF" and stops == "without stop words":
        return TfidfVectorizer(stop_words='english', ngram_range=(1, 3))


def setParameters():
    askForType()  # What type of n-gram will be tested?
    askForRepresentation()  # What representation of n-gram will be tested?
    askAboutStopWords()  # Are stop words included in the test?
    askForClassifier()  # What classifier does the user want?
    corpusVector = setVector(nGramType, representation, stops)  # Selects a vector based on the user's test preferences.
    fittedCorpusVector = corpusVector.fit_transform(corpus)  # Fits the n-gram configuration to the corpus of documents.
    corpusVectorAsArray = fittedCorpusVector.toarray()  # Puts the fitted data in an array.
    featureDescription = nGramType + " with " + representation + " representation and " + stops
    print("\nTEST SUMMARY\n" + "------------\n" + featureDescription)
    print("\nYou chose the following classifier:", classifier)
    print("\nPlease be patient - the program may take a while to run.")

    # Runs tests and displays results
    classificationResults(corpusVectorAsArray, documentClassifications, featureDescription)


# FUNCTION CALLS THAT EXECUTE WHENEVER THE PROGRAM IS RUN
loadData()
setParameters()
