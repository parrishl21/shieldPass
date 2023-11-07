# shieldPass

## Quick Notes

<ins>Make sure that the following are set on your local machine:</ins>
- Database is called 'shield_pass'
- Database hosted on the same machine as your code
- Database port is set to '5432'
- Database user called 'raywu1990' with password 'test'
- Database has all needed tables and triggers (inside of teams and GitHub)

## Quick Start

First, we need to install a Python 3 virtual environment with:
```
sudo apt-get install python3-venv
```

Create a virtual environment:
```
python3 -m venv python_venv
```

You need to activate the virtual environment when you want to use it:
```
source python_venv/bin/activate
```

To fufil all the requirements for the python server, you need to run:
```
pip3 install -r requirements.txt
```
Because we are now inside a virtual environment. We do not need sudo.

Then you can start the server with:
```
python3 main.py
```
