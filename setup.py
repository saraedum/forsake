# ********************************************************************
#  This file is part of forsake
#
#        Copyright (C) 2023 Julian Rüth
#
#  forsake is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  forsake is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with forsake. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

from distutils.core import setup

setup(
    name='forsake',
    version='0.1.0',
    packages=['forsake'],
    license='GPL 3.0+',
    description="TODO",
    long_description=open('README.md', encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
    install_requires=["click"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "forsake-server=forsake.cli:server",
            "forsake-client=forsake.cli:client"
        ],
    },
)
