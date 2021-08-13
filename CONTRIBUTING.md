# Contributing

## Get started
- Either **choose** an existing or **create** a new **issue** on GitHub.
- **Comment** on that issue (if it's an existing one). You'll then get the issue **assigned** to you.
- **Fork** & **Clone**

- **Code**. Make sure to follow our **Code Style** *(see section below this...)*.

- Create a new **branch** with a descriptive name.
- **Commit**, write an short & descriptive commit message. If you have things to add or questions you can add comments later on the pull request.
- **Push**
- Create a **pull request** and choose @Buscedv as the **reviewer**.
- Add a **reference** to the related issue(s) in the pull request as well.
- (You can also add **tags** if you want)

- If your PR is **approved** it will get merged either into `dev` or `master`.
- If it gets marked as **Changes requested**, do the chanages, **commit** & **push**, and request **re-review** by @Buscedv.

## Code style
- Use tabs.
- Use single quotes `'` and not double quotes `"`.
- If you have to use some sort of string formating use f-strings.
- Don't put unnecessary comments.
- But when you do add comments make sure that:
  - There is a space after the pund/hashtag.
  - The comment starts with a capital letter.
  - It ends with a full-stop/period.
- Follow the PEP8 guidelines, e.g. two empty lines between function definitions.
- A transpiled Ask program `app.py` should be able to run completely standalone. So all necessary functions, classes, utilities, etc. needs to be added to the transpiled code. This means no module importing in the output file!
