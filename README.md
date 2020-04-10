## Steps to run the App in local

## Make sure you have installed python3.7

### Install pip3
### pip3 install virtualenv

### virtualenv -p python3.7 devstory_env

## Activate the environment
## source ~/devstory_env/bin/activate

## Clone the project and go to the project directory 
### cd /devstory

### pip3 install -r requirements.txt
### python manage runserver

Go to http://localhost:8000/cron_job for the cron job to run and fetch the necessary details

Now open http://localhost:8000/dashboard to see the result