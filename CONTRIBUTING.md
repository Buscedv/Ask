# Contributing

## Get started
- Either **choose** an existing or **create** a new **issue** on GitHub.
- **Comment** on that issue (if it's an existing one). You'll then get the issue **assigned** to you.
- **Fork** & **Clone**

- **Code**. Make sure to follow our **Code Style** *(see section below this...)*.

- Create a new **branch** with a desriptive name.
- **Commit**, write a detailed but to the point commit message. If you have things to add or questions you can add comments later on the pull request.
- **Push**
- Create a **pull request** and choose @buscedv as the **reviewer**.
- Add a **reference** to the related issue(s) in the pull request as well.
- (You can also add **tags** if you want)

- If your PR is **approved** it will get merged either into `dev` or `master`.
- If it gets marked as **Changes requested**, do the chanages, **commit** & **push**, and request **re-review* by @buscedv

## Code style
- Use tabs.
- Use signle quotes `'` and not double quotes `"`.
- If you have to use some sort of string formating use f-strings.
- Don't put unneccesary comments.
- Follow the PEP8 guidelines, ex. two empty lines between methods.
- Ask is supposed to be in a single python script i.e. `ask.py`.
- A transpiled Ask program `app.py` should be able to run completely standalone. So all neccesary function, classes, utilities, etc. needs to be added to the transpiled code. This means no module importing.

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
