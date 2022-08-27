# tgfp-nfl
Python Package for scraping the external site's NFL data (scores, schedule, odds)

## Setting up project for development
* Install requirements from `dev_requirements.txt`
* Install `doppler`
* Create a shell configuration to run the script text
   * `doppler setup --config tst --project greatfootballpool`
* Add the following environment to the unit test:
   * `DOPPLER_ENV=1`