# Sitemap Generator [Python]
* Most of crawler source code is from **[Github](https://github.com/Haikson/sitemap-generator)**.

## How to run this
- `git clone https://github.com/suraw00t/sitemap-controller`
- `cd sitemap-controller`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install poetry`
- `poetry install`
- `./sctipts/run-controller`

sitemap.xml will be generated in current directory

## How to run this with docker compose
- `git clone https://github.com/suraw00t/sitemap-controller`
- `cd sitemap-controller`
- `docker compose up -d` or `docker-compose up -d (docker compose V.1)`

sitemap.xml will be generated in ../deployment/sitemap_controller directory