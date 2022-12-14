# Testing 

Test release: [Release ??](https://github.com/ibuttimer/soapbox/releases/tag/??? )

## Environment
If using a [Virtual Environment](../../README.md#virtual-environment), ensure it is activated. Please see [Activating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

> **Note:** Two separate testing frameworks are utilised [unittest](#unittest-unit-testing) and [Django Test Tools](#django-test-tools-unit-testing).
> Tests are _**not**_ interoperable between test frameworks. See [Unit Testing Summary](#unittest-unit-testing) for comparison.

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
The [.test-env](../../.test-env) is used to set up the environment.

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

## Test Coverage
Test coverage reports are generated using the [coverage](https://pypi.org/project/coverage/) utility, ands its configuration is specified in [.coveragerc](../../.coveragerc).
See [Unit Testing Summary](#unittest-unit-testing) for usage.

### Test Coverage Reports

| Framework                                            | Report                                                               |
|------------------------------------------------------|----------------------------------------------------------------------|
| [unittest](#unittest-unit-testing)                   | [Unittest test coverage report](doc/test/unittest_report/index.html) |
| [Django Test Tools](#django-test-tools-unit-testing) | [Django test coverage report](doc/test/django_report/index.html)     |

## Unit Testing Summary

| Environment                 | [unittest](https://docs.python.org/3/library/unittest.html)                         | [Django Test Tools](https://docs.djangoproject.com/en/4.1/topics/testing/tools/) |
|-----------------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **Location**                | [tests](../../tests/)                                                               | [django_tests](../../django_tests/)                                              |
| **Naming style**            | `*_test.py`                                                                         | `test_*.py`                                                                      |
| **Command**                 | `python -m unittest discover -p "*_test.py"`                                        | `python manage.py test`                                                          |
| **Coverage command**        | `coverage run -m unittest discover -p "*_test.py"`                                  | `coverage run manage.py test`                                                    |
| **Coverage report command** | `coverage html -d doc/test/unittest_report --title="Unittest test coverage report"` | `coverage html -d doc/test/django_report --title="Django test coverage report"`  |



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

The

node .\scrape.js -b http://127.0.0.1:8000/ -u user1 -p contrib1 -v user-profile


| Page    | HTML                                                                                            | HTML Result                                         | CSS                                                                                                                                                                                 | CSS Result                                          |
|---------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Landing | [W3C validator](https://validator.w3.org/nu/?doc=https%3A%2F%soapbox-opinions.herokuapp.com%2F) | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%soapbox-opinions.herokuapp.com%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | ![pass](https://badgen.net/badge/checks/Pass/green) |

## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/soapbox/issues).

#### Bug

[Bug list](https://github.com/ibuttimer/soapbox/labels/bug)

| Issue                                                           | Description                                      |
|-----------------------------------------------------------------|--------------------------------------------------|
