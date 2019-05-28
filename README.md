# Twitter fetcher

This software implements a Twitter fetcher that filters it content based on various queries to the Twitter API.
This product is one of various for my thesis project. 

Feel free to use it anytime, and any reference to the original author is welcome! :sunglasses:

## Requirements
In order to use this software you must install the following dependencies:
* Python 3.4+
* Twython 3.7+
* Unidecode 1.0.23+

You can install this requirements as:
```bash
python3 -m pip install twython unidecode
```

You must have a Twitter account as a Developer, this is done by sending a request of creating a new App in the platform,
this typically involves showing what are your intentions in using their API. After teh requests has been done, they 
will answer in aprox a day telling you that you have now permissions to use the API.

At this point you should be able to generate four (4) different tokens needed to execute this software:
* CONSUMER_KEY
* CONSUMER_SECRET
* ACCESS_TOKEN
* ACCESS_SECRET

## Execution
In order to execute this, first clone this repository and execute the software as:

```bash
git clone https://github.com/SkinMan95/pgr-twitter-fetcher.git
cd pgr-twitter-fetcher
python3 fetcher.py --consumer_key CONSUMER_KEY \
                   --consumer_secret CONSUMER_SECRET \
                   --access_token ACCESS_TOKEN \
                   --access_secret ACCESS_SECRET
```

Since there could be some network errors, active or passive, they could pose a problem for this software, so a mitigation to
this issue is to set it in an infinite loop, until Ctrl+C is issued by the user:
```bash
while true; do python3 fetcher.py ... ; sleep 1; done
```

By default, this software will append the output collected from Twitter to a file called *fetched.json*, each line is a json with the 
content of the tweets, including all it's metadata, if you want it to be saved with a different name or location use **-o file** 
cli option

In case you need help in the CLI, you can type:
```bash
python3 fetcher.py -h
```

## Author
**Alejandro Anzola**, Computer Science student

Escuela Colombiana de Ingenieria Julio Garavito

Bogota, Colombia
