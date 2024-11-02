# bookspider
Scrapy Tutorial - An open source and collaborative framework for extracting the data you need from websites.

# How to install (Ubuntu 20.04.5 LTS)

## Create Python virtual environments
```
sudo apt install python3.12-venv
python3 -m venv venv
source venv/bin/acrivate
```

## Create your Scrapy project
```
scrapy startproject bookvoed
```

## Build and run your first spider with:
```
cd bookvoed
scrapy genspider bookspider
scrapy crawl bookspider
```