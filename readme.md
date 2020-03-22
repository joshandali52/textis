# TextIs
This is repository for the text mining tool developed to support the curriculum design process described in http://www.curriculum-design.uni.li/. The tool is developed to perform text analysis on a corpus (html files) of online job advertisements. Other types of texts, however, can also be used as valid data source. It is part of the Erasmus+ project ["Text Mining for Curriculum Design for Multiple Information Systems Disciplines"](https://ec.europa.eu/programmes/erasmus-plus/projects/eplus-project-details/#project/2017-1-LI01-KA203-000083).

We provided two modules: BackEnd and FrontEnd.

BackEnd codes provide the necessary data (html files) preprocessing and our implementation of the text mining methods (eg. clustering).

FrontEnd codes provided the means to setup the web application for visualizations to aid the text analysis process of the curriculum design process.

TODO: Documentation
Full documentation of the tool is available at ...

# Installation
Install python. We developed and tested the project with python3.8:
https://www.python.org/downloads/

It is recommended to create a python virtual environment to use this project:
https://docs.python.org/3/library/venv.html

Install all packages using pip in the FrontEnd/requirements.txt
```
> pip install -r FrontEnd/requirements.txt 
```

TODO: HowTo generate data files...

Change into the following directory:
```
> cd BackEnd
```
Generate files necessary for the web application.
```
> python generateFrontEndFiles.py
```
describe howto, paths, nltk setup, ...

# Usage
The visualization is implemented as a wep application base on django 3.0. For more details read the official docs (https://docs.djangoproject.com/en/3.0/).
Change into the following directory:
```
> cd FrontEnd/webapp
```
Start the development server locally
```
> python manage.py runserver
```
Open in a web browser the following URL:
http://127.0.0.1:8000/textis/

# License
BSD 2-Clause License

Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
