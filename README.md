# python-twitter

## Instructions
### Setup

- Clone the repository to your local machine using "git clone https://github.com/ab17254/python-twitter.git" 

- Create an file named "config.py" in "/mining_twitter_data" and copy the content below

        consumer_key = "ADD KEY HERE"
        consumer_secret = "ADD KEY HERE"
        access_token = "ADD KEY HERE"
        access_secret = "ADD KEY HERE"
        
- Replace the placeholder text with twitter API keys

### data_collection.py

- Navigate to "/mining_twitter_data" in your command prompt
- Use "python data_collection.py -q bbc -d data" to run this script. This will run the srcipt seraching the term "bbc" in tweets and adding them to a file located in the data directory
            
            "-q" - Querey for what you are searching for
            "-d" - Output directory 


### preprocessing.py
- Navigate to "/mining_twitter_data" in your command prompt
