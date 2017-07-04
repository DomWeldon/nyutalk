# Setup: Download and Process Data

Previous: [Setup Database](/docs/01_setup_database.md)

## Setup Python Environment

Assuming you have python3 installed with pip3, create a `virtualenv` to install your dependencies into and run commands in. Use the code below to create virtualenv called `london_pubs` in the current directory:

    virtualenv -p python3 london_pubs

Now activate the virtualenv, in Linux/Mac, do this by:

    source london_pubs/bin/activate

Now install the dependencies:

    pip3 install -r requirements.txt

When you are

For Windows users who are stuck, [see here](https://virtualenv.pypa.io/en/stable/userguide/).

## Scrape Data from Beer in the Evening

We're now going to scrape search results from the website [Beer in the Evening](http://www.beerintheevening.com/pubs/results.shtml?l=London&show_comments=5&page=0), which is a source of user generated content about London pubs. To do this, use the following commands to change directory into `bitespider` (**B** eer **I** n **T** he **E** vening spider) and run the crawler.

    cd bitespider
    scrapy crawl bitescraper/bitescraper/pubspider
