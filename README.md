# PitStop Hub

#### Video Demo: <https://youtu.be/tM6mSWw6S7s>

## Description:

Formula 1 Knowledge Base Page

It allows you to monitor recent events, team race statistics and individual competitions.

- Competitions
  - Contains information on all Formula 1 competitions
- Teams
  - Contains data about current teams
- Races
  - It is divided into seasons
  - After selecting a season, it shows all the races that took place at that time
- Favorites
  - displays items that have been added to favorites

### Technologies used

- Flask (python)
- Bootstrap (css)
- SQLite (sql)

And of course html + javascript

### How to start

You need to install dependencies from requirements.txt

    pip install requirements.txt

You also need to create an .env file where your api key for the api-sports.io portal and your secret key are located

    API_KEY=<your api key>
    SECRET_KEY=<your secret key>

### Additional information

To start using it, you need to create an account, all data is encrypted and kept in the database

It is possible to switch between dark and light mode

### Update

Recently, restrictions have been introduced on the free use of the API, so to get all the data you need to purchase the full version of this API

However, the free version includes data from 2021-2023.
