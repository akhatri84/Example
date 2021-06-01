# True Cost Label  - Backend

## Table of Contents

[OVERVIEW](#overview)  

[GETTING STARTED](#gettingstarted)

[PREREQUISITES](#prerequisites)

[INSTALLING](#installing)

[RUNING AND TEST](#runningandtest)

[DEPLOYMENT](#deployment)

[BUILD WITH](#buildwith)

[TOOLS & METHODOLOGY](#tools&methodology)

[VERSIONING](#versioning)

[AUTHORS](#authors)

[ACKNOWLEDGMENTS](#acknowledgments)

<a name="overview"/></a>


## OVERVIEW

True Cost Label will become a collection of brands that choose radical transparency for their storytelling. In order to achieve this transparency, we work together with brands to quantify the impact of their products. This allows consumers not only to look at price and design when considering what products to buy but also to look at the various environmental costs involved. Not only will we help consumers finding products that meet all their desires, but we will also provide them with interesting content about their favorite brands. This will further increase the appreciation of products.

## GETTING STARTED

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

```
git clone https://github.com/vikpande/tcl-backend.git
```
Create virtual environmental on macOS and Linux:

```
python3 -m venv env
```
Create virtual environmental On Windows:

```
py -m venv env
```

Activate Virtual environmental :

```
Project root > .\env\Scripts\activate
```

Installing require packages in Virtual environment :

```
(env) Project root > pip install -r requirements.txt
```

NOTE :

When any new package added peform below command to add package detail in requirements.txt

```
(env) Project root > pip freeze > requirements.txt
```


## PREREQUISITES

Before you begin with setup, ensure the following is installed to your system:

* [Python 3.8 or greater]
* [Python Pip, the package manager]
* [Docker]
* [Git and a GitHub account]

### INSTALLING

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
python manage.py runserver
```
Runs the app in the development mode.
Open http://127.0.0.1:8000/ to view it in the browser.

## RUNING AND TEST

Explain how to run the automated tests for this system


## DEPLOYMENT

To deploy the application over EBS Environment follow the below steps.

### Prerequisites

Before you proceed you need to have an AWS IAM user credentials to deploy the application seamlessly from your local system to EBS. Please connect with admin to get the AWS user access credentials.

To follow the deployment procedure, you should have all of the Common Prerequisites for Python installed, including the following packages:

* Python 3.7.6 - AWS EBS supported latest python version
* pip
* virtualenv
* [awsebcli](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) -AWS Elastic Beanstalk cli required to push changes to cloud environment
* requirements.txt - Ensure this file remain upto date before starting the deployment and should be placed under root of project directory ` ~/tcl-backend/Tcl/requirements.txt`


### Configure your local application workspace for Elastic Beanstalk

Once you have installed the awsebcli and got the IAM credentials it's time for configuring the aws eb cli to do so run the following command.

Review in progress will update the steps after finalising the deployment pattern....



## BUILD WITH

* [Python](https://www.python.org/) - The backend framework used
* [Django](https://www.djangoproject.com/) - Python web Framework
* [Nginx](https://www.nginx.com/) - Web Server
* [Gunicorn](https://gunicorn.org/) - A WSGI application server
* [Postgresql](https://www.postgresql.org/) - Database System
* [GraphQL](https://graphql.org/) - Graph Query Language
* [ORM](https://www.sqlalchemy.org/) - Sqlalchemy
* [AWS](https://aws.amazon.com/) - Cloud Hosting


## TOOLS & METHODOLOGY

- [x] Trello was used to track progress of build (see Project Plan above).
- [x] Code was reviewed by myself, other Team members
- [x] Frequent commits (over 100), pull requests, and documentation updates were made.
- [x] Agile development methodologies were utilised.
- [x] Postgresl database was used.


## VERSIONING

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## AUTHORS

* **Nirav Kukadiya** - *Initial work* - [Nirav Kukadiya](https://github.com/nkukadiya89)
* **Vikas Pandey** - *Helping and Guide* - [Vikas Pandey](https://github.com/vikpande)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.


## ACKNOWLEDGMENTS

* Hat tip to anyone whose code was used
* Inspiration
* etc
