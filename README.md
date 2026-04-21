# Text-Based Adventure Game Creating (T-BAC) Website

A Django project that provides a website for both playing and creating text-based adventure games.

## Building the project
Run these commands:
```
python pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Then visit `127.0.0.1:8000` in your browser and login with the credentials you created in the setup step.
## Importing an example
You can create new games from scratch by navigating to the "My Games" page in the "Profile" Dropdown and clicking "+ new game" but if you wish to import an example game there is one included in the project.
On the "My Games" page click "import game" and select `example_game_export.json` in the project folder. You should then find a new game in your list of games called "A Queen's Quest". Select it and click
the publish link under the game name. You can play around with the game setup at this point and see how it all fits together or you can navigate back to the homepage and play the game.
