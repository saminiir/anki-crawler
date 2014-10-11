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
        print self.deck
        if self.card_type == "basic":
            return {
                'data': "[[\"{0}\",\"{1}\"],\"\"]".format(self.question, self.answer),
                'mid': AnkiCard.BASIC_ID,
                'deck': self.deck
            }
        else:
            return {
                'data': "[[\"{0}\",\"\"],\"\"]".format(self.question),
                'mid': AnkiCard.CLOZE_ID,
                'deck': self.deck
            }

    def __str__(self):
        return "Card type: {0}, question: {1}, answer: {2}, deck: {3}".format(
                self.card_type, self.question, self.answer, self.deck)

    def __repr__(self):
        return "Card type: {0}, question: {1}, answer: {2}, deck: {3}".format(
                self.card_type, self.question, self.answer, self.deck)

def parse_card(f):
    for line in f:
        card_type = f.next()

        #question: tag
        f.next()

        question = ""
        answer = ""

        deck = ""

        while True:
            tmp = f.next()

            if "ANSWER:" in tmp:
                break

            question += tmp

        while True:
            tmp = f.next()

            if "DECK:" in tmp:
                break

            answer += tmp

        deck = f.next()

        f.next()

        yield AnkiCard(card_type.strip(), question.strip().replace('\n', "<br/>"),
                       answer.strip().replace('\n', "<br/>"), deck.strip()) 

def main(args):
    with open(args.file, 'r') as f:
        file_iter = iter(f)

        cards = [card for card in parse_card(f)]

        add_cards_to_anki(cards, args.username, args.password)

def add_cards_to_anki(cards, username, password):
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

        print payload

        r = s.post("https://ankiweb.net/edit/save", data=payload)

        time.sleep(1)

    r = s.get("https://ankiweb.net/account/logout")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a file of anki-cards and sends them to AnkiWeb")
    parser.add_argument('-f', type=str, dest="file", required=True, help="The location of the ankicards file")
    parser.add_argument('-u', type=str, dest="username", required=True, help="Anki username")
    parser.add_argument('-p', type=str, dest="password", required=True, help="Anki password")
    args = parser.parse_args()
    main(args)
