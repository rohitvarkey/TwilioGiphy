from twilio.rest import TwilioRestClient
import requests

def sendTwilioMMS(client, toPhoneNumber, message, media_url, fromPhone):
    message = client.messages.create(
        body=message,
        to=toPhoneNumber,
        from_=fromPhone,
        media_url=media_url
    )
    #TODO: Add checks for errors.
    #TODO: Add logging.
    print message
    return message

def getGifUrlForTerm(term):
    gif = requests.get(
        "http://api.giphy.com/v1/gifs/translate",
        params = {"s":term, "api_key": "dc6zaTOxFJmzC"}
    )
    return gif.json()["data"]["images"]["original"]["url"]

def sendTwilioGIF(client, toPhoneNumber, message, term, fromPhone):
    url = getGifUrlForTerm(term)
    message = sendTwilioMMS(client, toPhoneNumber, message, url, fromPhone)
    return message, url
