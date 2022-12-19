# Testing

## Pre-test setup
### Users
Manually created the following users required for testing purposes:

| Username | Group     |
|----------|-----------|
| user1    | Author    |
| user2    | Author    |
| user3    | Author    |
| mod1     | Moderator |

Login as [site administrator](../../README.md#create-a-superuser) and assign `mod1` to the Moderators group via their profile page, or
alternatively via the [Django administration site](https://soapbox-opinions.herokuapp.com/admin/login/?next=/admin/)

### Database
Populate the database with predefined opinions and comment via the [populate.py](data/populate.py) script.
When run using [run_populate.py](run_populate.py) it will load the opinions from [opinions.csv](data/opinions.csv) and generate comments.

From the project root folder run the following
```bash
# Help listing
python run_populate.py -h

# E.g. populated the remote database (replace 'password' as appropriate) 
python run_populate.py -up password -mp password -dv REMOTE_DATABASE_URL
```

## Environment
If using a [Virtual Environment](../../README.md#virtual-environment), ensure it is activated. Please see [Activating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

## Testing
Three separate testing frameworks are utilised [unittest](#unittest-unit-testing), [Django Test Tools](#django-test-tools-unit-testing)
and [Jest Unit Testing](#jest-unit-testing).

> **Note:** Tests are _**not**_ interoperable between test frameworks. See [Unit Testing Summary](#unittest-unit-testing) for comparison.

The site was tested using the following methods:

## Unittest Unit Testing
Unit testing of scripts was undertaken using [unittest](https://docs.python.org/3/library/unittest.html#module-unittest).
The test scripts are located in the [tests](../../tests/) folder, and the naming format is `*_test.py`.

**Note:** [Environment](#environment)

The tests may be run from the project root folder:
```shell
Run all tests
> python -m unittest discover -p "*_test.py"

Run an individual test, e.g.
> python -m unittest tests/user/test_forms.py
```
Alternatively, if using:
* Visual Studio Code

  The [Test Explorer UI](https://marketplace.visualstudio.com/items?itemName=hbenl.vscode-test-explorer) or Visual Studio Code's native testing UI<sup>*</sup>, allows tests to be run from the sidebar of Visual Studio Code.
* IntelliJ IDEA

  The allows tests to be run from the Project Explorer of IntelliJ IDEA.

<sup>*</sup> Set `testExplorer.useNativeTesting` to `true` in the Visual Studio Code settings.

## Django Test Tools Unit Testing
Unit testing of views was undertaken using [Django Test Tools](https://docs.djangoproject.com/en/4.1/topics/testing/tools/).
The test scripts are located in the [django_tests](../../django_tests/) folder, and the naming format is `test_*.py`.

**Note 1:** [Environment](#environment)

**Note 2:** Running the test full suite can take 5-6 minutes

**It is necessary to specify a number of environment variables prior to running tests.**
The [.test-env](.test-env) configuration file provides the necessary settings, and may be utilised by setting the `ENV_FILE` environment variable.
```shell
Powershell
> $env:ENV_FILE='.test-env'

Windows
> set ENV_FILE=.test-env

Linux
> export ENV_FILE='.test-env'
```
The tests may be run from the project root folder:
```shell
Run all tests
> python manage.py test

Run an individual test, e.g.
> python manage.py test django_tests.base.test_landing_view
```

## Jest Unit Testing
Javascript unit testing was undertaken using [Jest](https://jestjs.io/), combined with [Puppeteer](https://pptr.dev/) to 
provide the browser automation to retrieve the page content.

The test scripts are located in the [jest_tests](../../jest_tests/) folder, and the naming format is `*.spec.js`.

**Note 1:** [Environment](#environment)

**Note 2:** The test server need to be running prior to executing tests.

Create a configuration file called `test_config.json` in the [jest_tests](../../jest_tests/) folder, based on [sample_test_config.json](../../jest_tests/sample_test_config.json)

The tests may be run from the project root folder:
```shell
Run all tests
> npm test
```

## Test Coverage
Test coverage reports are generated using the [coverage](https://pypi.org/project/coverage/) utility, ands its configuration is specified in [.coveragerc](../../.coveragerc).
See [Unit Testing Summary](#unittest-unit-testing) for usage.

### Test Coverage Reports

| Framework                                            | Report                                                               |
|------------------------------------------------------|----------------------------------------------------------------------|
| [unittest](#unittest-unit-testing)                   | [Unittest test coverage report](doc/test/unittest_report/index.html) |
| [Django Test Tools](#django-test-tools-unit-testing) | [Django test coverage report](doc/test/django_report/index.html)     |
| [Jest Unit Testing](#jest-unit-testing)              | n/a as testing was performed using automated browser interaction     |

## Unit Testing Summary

| Environment                 | [unittest](https://docs.python.org/3/library/unittest.html)                         | [Django Test Tools](https://docs.djangoproject.com/en/4.1/topics/testing/tools/) | [Jest Unit Testing](#jest-unit-testing) |
|-----------------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|-----------------------------------------|
| **Location**                | [tests](../../tests/)                                                               | [django_tests](../../django_tests/)                                              | [jest_tests](../../jest_tests/)         |
| **Naming style**            | `*_test.py`                                                                         | `test_*.py`                                                                      | `*.spec.js`                             |
| **Command**                 | `python -m unittest discover -p "*_test.py"`                                        | `python manage.py test`                                                          | `npm test`                              |
| **Coverage command**        | `coverage run -m unittest discover -p "*_test.py"`                                  | `coverage run manage.py test`                                                    | n/a                                     |
| **Coverage report command** | `coverage html -d doc/test/unittest_report --title="Unittest test coverage report"` | `coverage html -d doc/test/django_report --title="Django test coverage report"`  | n/a                                     |



## PEP8 Testing
[PEP8](https://peps.python.org/pep-0008/) compliance testing was performed using [pycodestyle](https://pypi.org/project/pycodestyle/)

**Note:** [Environment](#environment)

The tests may be run from the project root folder:
```shell
Run all tests
> pycodestyle .

Run an individual test, e.g.
> pycodestyle user/forms.py 
```

The basic pycodestyle configuration is contained in [setup.cfg](../../setup.cfg). See [Configuration](https://pycodestyle.pycqa.org/en/latest/intro.html#configuration) for additional configuration options.

> **Note:** PEP8 testing is also performed as part of the unit test suite, see [test_style.py](../../tests/style_test.py).
> When running unit tests from the terminal, it may be disabled by setting the `SKIP_PEP8` environment variable to `y` or `n`.

```shell
For Linux and Mac:                            For Windows:
$ export SKIP_PEP8=y                          > set SKIP_PEP8=y
```

## Manual
The site was manually tested in the following browsers:

|     | Browser                                   | OS                          | 
|-----|-------------------------------------------|-----------------------------|
| 1   | Google Chrome, Version 104.0.5112.81      | Windows 11 Pro Version 21H2 |
| 2   | Mozilla Firefox, Version 103.0.2 (64-bit) | Windows 11 Pro Version 21H2 |
| 3   | Opera, Version:89.0.4447.91               | Windows 11 Pro Version 21H2 |

Testing undertaken:

| Feature                                             | Expected                                                  | Action                                                                                                                                        | Related                                                                            | Result                                              | 
|-----------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------|

Test coverage:
| Framework

## Responsiveness Testing


## Lighthouse


## Accessibility

## User


## Validator Testing

The [W3C Nu Html Checker](https://validator.w3.org/nu/) was utilised to check the HTML validity, while the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) was utilised to check the CSS validity with respect to [CSS level 3 + SVG](https://www.w3.org/Style/CSS/current-work.html.)

> **Note:** The following third party artifacts fail the W3C Validator tests: 
> - [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) checks
>   - [Bootstrap v5.2.3](https://www.jsdelivr.com/package/npm/bootstrap) minified css files
>   - [Font Awesome](https://github.com/FortAwesome/Font-Awesome) minified css files
> - [W3C Nu Html Checker](https://validator.w3.org/nu/)
>   - [django-summernote](https://pypi.org/project/django-summernote/) HTML
> 
> Consequently, these elements have been excluded (via test-specific urls) from the page content tested to produce the results in the following table.

Where possible content was validated via the URI methods provided by the validators. However this was not possible for pages which required the client to be logged in.
In this case, the content (accessed via special test urls to exclude Bootstrap and Font Awesome css files) was scraped using [scrape.js](data/scrape.js) and saved in the [doc/test/generated](doc/test/generated) folder.
The resultant file was used to validate the content via the file upload methods provided by the validators.

| Page                                 | HTML                                                                                                                                                 | HTML Result                                         | CSS                                                                                                                                                                                                       | Scrape args <sup>**</sup><br>(Excluding host & credentials) | Scraped file                                                                                           | CSS Result                                          |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Landing                              | [W3C validator](https://validator.w3.org/nu/?doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2F&showsource=yes&showoutline=yes)                     | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)             | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Signin                               | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Faccounts%2Flogin%2F)  | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test%2Flogin%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)  | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Register                             | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Faccounts%2Fsignup%2F) | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test%2Fsignup%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v user-profile-val-test                                    | [user-profile-val-test.html](generated/user-profile-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Logout                               | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v logout-val-test                                          | [logout-val-test.html](generated/logout-val-test.html)                                                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Following feed                       | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v following-val-test                                       | [following-val-test.html](generated/following-val-test.html)                                           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Category feed                        | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v category-val-test                                        | [category-val-test.html](generated/category-val-test.html)                                             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Read opinion                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-read-val-test --io 40                            | [opinion-read-val-test.html](generated/opinion-read-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion list                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinions-all-val-test                                    | [opinions-all-val-test.html](generated/opinions-all-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| New opinion                          | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-new-val-test                                     | [opinion-new-val-test.html](generated/opinion-new-val-test.html)                                       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Edit opinion                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-edit-val-test --io 33                            | [opinion-edit-val-test.html](generated/opinion-edit-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment list                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v comments-all-val-test                                    | [comments-all-val-test.html](generated/comments-all-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending list        | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinions-pending-val-test                            | [mod-opinions-pending-val-test.html](generated/mod-opinions-pending-val-test.html)                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending pre-assign  | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinion-review-pre-assign-val-test --po 51           | [mod-opinion-review-pre-assign-val-test.html](generated/mod-opinion-review-pre-assign-val-test.html)   | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending post-assign | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinion-review-post-assign-val-test --uo 55          | [mod-opinion-review-post-assign-val-test.html](generated/mod-opinion-review-post-assign-val-test.html) | ![pass](https://badgen.net/badge/checks/Pass/green) |

<sup>*</sup> Link not available as not being logged results in redirect to login page 

<sup>**</sup> See [Content scraping](#content-scraping) 

### Content scraping

The [scrape.js](data/scrape.js) script may be used to scrape page content.
It is provided so that content requiring the client to be logged in may be retrieved quickly with minimal manual user input.

From the [data](data) folder run the following
```bash
# Help listing
node .\scrape.js --help
 
# List if views which may be scraped 
node .\scrape.js -l

# E.g. scrape logout page (replace 'user' and 'password' as appropriate 
node .\scrape.js -b https://soapbox-opinions.herokuapp.com/ -u user -p password -v logout-val-test
```

## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/soapbox/issues).

#### Bug

[Bug list](https://github.com/ibuttimer/soapbox/labels/bug)

| Issue                                                           | Description                                      |
|-----------------------------------------------------------------|--------------------------------------------------|
