UQx API
======== 
The UQx API is a REST API for taking injested edX research package and making it available for services to leverage.  The API
supports OAuth2 and Basic authentication.  

The ingested databases are designed to work in conjunction with the injestor application: https://github.com/UQ-UQx/injestor.  The UQx API
can be used to provide data to any number of services, one of which is the Dashboard - https://github.com/UQ-UQx/dashboard_js.


Requirements
---------------------
The API should be run on a webserver such as apache on nginx, and be used on a server running mysql and mongo databases which are
being populated by the injestor application: https://github.com/UQ-UQx/injestor.

Installation
---------------------
[BASE_PATH] is the path where you want the UQx_API installed (such as /var/www/html/api)

Clone the repository
```bash
git clone https://github.com/UQ-UQx/uqx_api.git [BASE_PATH]
```
Install pip requirements
```bash
pip install -r requirements.txt
```
Set UQx API configuration
```bash
cp [BASE_PATH]/config.example.py [BASE_PATH]/config.py
vim [BASE_PATH]/config.py
[[EDIT THE VALUES]]
```
Set the courses to provide an API for
```bash
vim [BASE_PATH]/uqx_api/courses.py
```
Create the api database in your MySQL installation
```bash
mysql -u root -p
MAKE API DATABASE > mysql > CREATE DATABASE api;
```
Configure your web server to run the application, see http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html for more details.
A preconfigured uwSGI configuration can be found in the wsgi directory, you can use this with nginx by:
```bash
ln -s [BASE_PATH]/wsgi/uqx_api_nginx.conf /etc/nginx/sites-enabled/uqx_api_nginx.conf
```
Check the configuration files in [BASE_PATH]/wsgi for detailed customisation.

Architecture
---------------------
The architecture of the UQx API follows django conventions and relies on the django-rest-framework framework.  The /api application contains the API.  
APIs are added within the /api/views.py file (inside endpoints()), which then calls the appropraite class/method inside /api/apis.  For example, "student_ages"
in the endpoints() calls the method genders() within /api/apis/students.py.

The flow of the data is as follows:
![UQx API Architecture](/README_ARCHITECTURE_IMAGE.png?raw=true "UQx API Architecture")

Running Tests
---------------------
Currently the project is at an early stage and does not have reliable tests created.

License
---------------------
This project is licensed under the terms of the MIT license.

How to Contribute
---------------------
Currently the injestor project is at a very early stage and unlikely to accept pull requests
in a timely fashion as the structure may change without notice.
However feel free to open issues that you run into and we can look at them ASAP.

Contact
---------------------
The best contact point apart from opening github issues or comments is to email 
technical@uqx.uq.edu.au