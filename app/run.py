# -*- coding: utf-8 -*-

from mastodon import Mastodon, CallbackStreamListener, MastodonAPIError, MastodonRatelimitError
import subprocess
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Import keys from .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DOMAIN = os.environ.get("DOMAIN")
MAIL_ADDR = os.environ.get("MAIL_ADDR")
PASSWORD = os.environ.get("PASSWORD")

# Generate Mastodon objects
if (os.path.isfile('clientcred.secret') == False):
    Mastodon.create_app(
        'markov-from-tweet',
        api_base_url=DOMAIN,
        to_file='clientcred.secret'
    )
if (os.path.isfile('usercred.secret') == False):
    m = Mastodon(
        client_id='clientcred.secret',
        api_base_url=DOMAIN
    )
    m.log_in(
        MAIL_ADDR,
        PASSWORD,
        to_file='usercred.secret'
    )
api = Mastodon(
    access_token='usercred.secret',
    api_base_url=DOMAIN
)

# Run generator


def res_cmd(cmd):
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        shell=True).communicate()[0]

# Remove risky words from result


def remover(result):
    # Load banned.json
    json_open = open('data/banned.json', 'r')
    json_load = json.load(json_open)
    # Delete detected words from original sentences
    for w in json_load['words']:
        result = result.replace(w, '')
    return result


def main():
    # Get original sentences generated from markov-chains
    # Run text_generator.py to get sentence.
    cmd = ("python3 text_generator.py")
    # Put the generated sentence into 'result' variable
    result = res_cmd(cmd)
    result = result.decode()

    # Remove risky words from result
    result = remover(result)

    # Call Twitter API to tweet
    try:
        api.status_post(result)
    except MastodonAPIError as e:
        print(e)


if __name__ == '__main__':
    main()
