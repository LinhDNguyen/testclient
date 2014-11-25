#
# python module SettingReader.py
#
# Version: 0.0.1
# Author:  Nguyen Linh
# Contact: nvl1109@gmail.com
# License: MIT License
#
# Tested with python 2.7 and 3.2
#
# Copyright (c) 2013 Alejandro Lopez Correa
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import print_function # just for test() function at the end
import xml.dom.minidom

# -------------------------------------------------------------------
# SettingReader: main class that deals with xml dom
# xml config file syntax
"""
<configs>
    <name>Test station 1</name>
    <compilers>
        <compiler name='iar'>C:/iar</compiler>
        <compiler name='uv4'>C:/uv4</compiler>
        <compiler name='kds'>C:/kds</compiler>
    </compilers>
    <specific_config>
    jsut a confit
    </specific_config>
</configs>
"""
class SettingReader( object ):


