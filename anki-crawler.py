import requests
import time
import argparse

import logging
import httplib

httplib.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

class AnkiCard(object):
    BASIC_ID = 1408344581768
    CLOZE_ID = 1408344581765

    def __init__(self, card_type, question, answer, deck):
        self.card_type = card_type
        self.question = question
        self.answer = answer
        self.deck = deck

    def format(self):
        """Format card to POST payload required by AnkiWeb"""

        # AnkiWeb needs some custom formatting
        card_type = self.card_type.strip()
        question = self.question.strip().replace('\n', "<br/>").replace('"', '\\"')
        answer = self.answer.strip().replace('\n', "<br/>").replace('"', '\\"')
        deck = self.deck.strip()

        if card_type == "basic":
            return {
                'data': "[[\"{0}\",\"{1}\"],\"\"]".format(question, answer),
                'mid': AnkiCard.BASIC_ID,
                'deck': deck
            }
        else:
            return {
                'data': "[[\"{0}\",\"\"],\"\"]".format(question),
                'mid': AnkiCard.CLOZE_ID,
                'deck': deck
            }

    def __str__(self):
        return "Card type: {0}, question: {1}, answer: {2}, deck: {3}".format(
                self.card_type, self.question, self.answer, self.deck)

    def __repr__(self):
        return "Card type: {0}, question: {1}, answer: {2}, deck: {3}".format(
                self.card_type, self.question, self.answer, self.deck)


def add_cards_to_anki(cards, username, password):
    """Adds the given cards to the AnkiWeb server"""
    s = requests.Session()
    r = s.get("https://ankiweb.net/account/login")

    time.sleep(1)

    login_payload = { 'submitted': 1, 'username': username, 'password': password }

    r = s.post("https://ankiweb.net/account/login", data=login_payload)

    time.sleep(1)

    for card in cards:
        r = s.get("https://ankiweb.net/edit/")

        time.sleep(1)

        payload = card.format()

        r = s.post("https://ankiweb.net/edit/save", data=payload)

        time.sleep(1)

    r = s.get("https://ankiweb.net/account/logout")

def parse_multiline_string(f, end_block):
    """Parses a multiline-string from file, with
    a terminator end block.
    """
    multiline_string = ""
    while True:
        tmp = f.next()

        if end_block in tmp:
            break

        multiline_string += tmp

    return multiline_string

def parse_card(f):
    """Parses an anki-card from file"""
    for line in f:
        card_type = f.next()

        f.next() #question-tag

        question = parse_multiline_string(f, "ANSWER:")
        answer = parse_multiline_string(f, "DECK:")

        deck = f.next()

        f.next() #skip empty line after card

        yield AnkiCard(card_type, question, answer, deck) 

def main(args):
    with open(args.file, 'r') as f:
        cards = [card for card in parse_card(f)]

        add_cards_to_anki(cards, args.username, args.password)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a file of anki-cards and sends them to AnkiWeb")
    parser.add_argument('-f', type=str, dest="file", required=True, help="The location of the ankicards file")
    parser.add_argument('-u', type=str, dest="username", required=True, help="Anki username")
    parser.add_argument('-p', type=str, dest="password", required=True, help="Anki password")
    args = parser.parse_args()
    main(args)
