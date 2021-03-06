Remote JS Slide Show
====================

A Javascript/Python remote slide show.


Install:
--------

For debian like distributions

    sudo apt-get install python-qt4 python-qt4-dev python-poppler-qt4 libpoppler-qt4-dev
    cd third_party/pypoppler-qt4/
    python configure.py
    sudo make install

Installing python modules : `autobahn twisted`
Warning, you must have installed the python's package manager. `python-pip`

    sudo pip install autobahn[twisted,accelerate]


Running:
--------

    cd server/
    python remoteServerd.py

Now you can open the webapp from `web/index.html` and have some fun !




License:
--------

    This software is under MIT Licence
    Copyright (C) 2014 Skander Ben Mahmoud \<skander.benmahmoud@esprit.tn\>
    
    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all copies
    or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
    AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
