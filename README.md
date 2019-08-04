# CSV Manager
CartoView App for uploading and publishing layers from CSV files to GeoNode and GeoServer

Using Django to develop the backend logic and ReactJS for the front end logic.
You will find comments all over the 

## Backend Project Structure (Django):

#### Using the following command to simply create a django app using cartoview app template:

```sh
$ django-admin startapp --template=https://github.com/cartologic/Cartoview-app-template/archive/master.zip <your_App_name>
```

### Basic Django app development contains mainly the following parts:
-   Models `models.py`
-   Views `views.py`
-   Templates `templates directory`
-   Static `static directory` 
-   Migrations `migrations directory` 
-   URLs `urls.py`
-   Admin Panel `admin.py`
-   Initial App configuration `apps.py` & `__init__.py`

### Additionally Created an API using tastypie
-   api `api.py`

### Additional helper files:
-   `utils.py`
-   `helpers.py`
-   `signals.py`

### Separated Logic Files
-   `logic.py`
-   `publishers.py`

## Frontend Project (ReactJS):
### Directory Structure:
-   webpack config `webpack.config.js` & `webpack.config.production.js`
-   `package.json`
-   `.babelrc` 
-   Source Code `src directory`
-   Build Files `dist directory`

### `src directory`
-   The main entry point `index.js`
-   containers directory contains `CSVManager.jsx` which the brain of the App
-   components contains UI dummy components that receive only props and updates from `CSVManager.jsx`
-   utils Directory contains 