import re


# Wrapper because I plan to add more formatting functions
def format(text):
    text = add_backticks_to_sentences(text)

    return text


def add_backticks_to_sentences(text):
    sentences = re.split("(?<=[.!?]) +", text)

    modified_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 0:
            # Check if the last word has trailing punctuation
            if words[-1][-1] in ".!?":
                # If it does, add the backticks before the punctuation
                words[-1] = f"`{words[-1][:-1]}`{words[-1][-1]}"
            else:
                # If it doesn't, add the backticks around the word
                words[-1] = f"`{words[-1]}`"
        modified_sentences.append(" ".join(words))

    return " ".join(modified_sentences)
