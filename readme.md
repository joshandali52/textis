# TextIs
The software in this repo supports the curriculum design process using job ad analysis described at http://www.curriculum-design.uni.li/. The tool is developed to perform text analysis on a corpus (html files) of online job advertisements. Other types of texts, however, can also be used as valid data source. It is part of the Erasmus+ project ["Text Mining for Curriculum Design for Multiple Information Systems Disciplines"](https://ec.europa.eu/programmes/erasmus-plus/projects/eplus-project-details/#project/2017-1-LI01-KA203-000083).

<img src="logo/erasmus.jpg" width="200">

The software contains a web-based frontend and a backend for analysing job ads (html or txt files).

The BackEnd does preprocessing/cleaning and the text mining methods. It provides files used by the FrontEnd

The FrontEnd is a web application for visualization and query of data from the backend.

TODO: Documentation
Full documentation of the tool is available at ...

# Installation
Install python 3.6 or higher:
https://www.python.org/downloads/

It is recommended to create a python virtual environment to use this project:
https://docs.python.org/3/library/venv.html

Install all packages using pip in the FrontEnd/requirements.txt
```
> pip install -r FrontEnd/requirements.txt 
```

TODO: ntlk setup

Set path of the raw data (html files) in Config.py (rpath). In this repository we provided an example dataset in the data folder and set the rpath variable as follows:
```
self.rpath = "../data/"
```

Generate files necessary for the web application and return to the root directory:
```
> cd BackEnd
> python generateFrontEndFiles.py
> cd ..
```

# Usage
The visualization is implemented as a wep application base on django 3.0. For more details read the official docs (https://docs.djangoproject.com/en/3.0/).
Change into the following directory:
```
> cd FrontEnd
```
Start the development server locally
```
> python webapp/manage.py runserver
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
