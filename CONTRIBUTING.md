# Contributing

## Code style
- Use tabs.
- Use single quotes `'` and not double quotes `"`.
- If you have to use some sort of string formating use f-strings.
- Don't put unneccesary comments.
- Follow the PEP8 guidelines, ex. two empty lines between methods.
- Ask is supposed to be in a single python script i.e. `ask.py`.
- A transpiled Ask program `app.py` should be able to run completely standalone. So all neccesary function, classes, utilities, etc. needs to be added to the transpiled code. This means no local module importing.

## Dev environment
1. Create a vritual environment:
- `python3 -m venv venv`
2. Activate it:
- `source venv/bin/activate`
3. Install dependencies:
- `pip install -r requirements.txt`

**When running ask**

4. Get helpful info and debug messages:

- Run ask with the `-d` flag.
  - `python3 ask.py [my file].ask -d`
