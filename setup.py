#!/usr/bin/env python3

# PytgVoIP-Pyrogram - Pyrogram support module for Telegram VoIP Library for Python
# Copyright (C) 2020 bakatrouble <https://github.com/bakatrouble>
#
# This file is part of PytgVoIP.
#
# PytgVoIP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PytgVoIP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PytgVoIP.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from setuptools import setup


def get_version():
    with open('tgvoip_pyrogram/__init__.py', encoding='utf-8') as f:
        version = re.findall(r"__version__ = '(.+)'", f.read())[0]
        if os.environ.get('BUILD') is None:
            version += '+develop'
        return version


def get_long_description():
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name='pytgvoip_pyrogram',
    version=get_version(),
    license='LGPLv3+',
    author='bakatrouble',
    author_email='bakatrouble@gmail.com',
    description='Pyrogram support module for Telegram VoIP Library for Python',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/bakatrouble/pytgvoip_pyrogram',
    keywords='telegram messenger voip library python pyrogram',
    project_urls={
        'Tracker': 'https://github.com/bakatrouble/pytgvoip_pyrogram/issues',
        'Community': 'https:/t.me/pytgvoip',
        'Source': 'https://github.com/bakatrouble/pytgvoip_pyrogram',
    },
    python_required='~=3.5',
    packages=['tgvoip_pyrogram'],
    install_requires=[
        'pytgvoip >= 0.0.7',
        'pyrogram >= 1.0.0'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Communications',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
