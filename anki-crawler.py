import requests

CLOZE_ID = 1408344581765
BASIC_ID = 1408344581768

def main():
    r = requests.get("https://ankiweb.net/account/login")

    print r.text

if __name__ == "__main__":
    main()
