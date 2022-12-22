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
| 1   | Google Chrome, Version 108.0.5359.125     | Windows 11 Pro Version 22H2 |
| 2   | Mozilla Firefox, Version 108.0.1 (64-bit) | Windows 11 Pro Version 22H2 |
| 3   | Opera, Version:94.0.4606.38               | Windows 11 Pro Version 22H2 |

Testing undertaken:

| Feature                                           | Expected                                                                                                                                                             | Action                                                                                                                                                                                                                                                                             | Related                      | Result                                              | 
|---------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|-----------------------------------------------------|
| Navbar `Logo`                                     | Clicking opens Landing page                                                                                                                                          | Click `Logo` button                                                                                                                                                                                                                                                                | All pages                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Navbar `Help`                                     | Clicking opens Help page                                                                                                                                             | Click `Help` menu button                                                                                                                                                                                                                                                           | All pages                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | Clicking Landing page `Register` and navbar `Register` menu button opens Register page                                                                               | Click Landing page `Register` and navbar `Register` menu button                                                                                                                                                                                                                    | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to manually register after entering all required info                                                                                                      | Enter user info on Registration page                                                                                                                                                                                                                                               | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to register using third party account (Google)                                                                                                             | Click `Sign In` menu button and use `Google` button to register                                                                                                                                                                                                                    | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to register using third party account (Twitter)                                                                                                            | Click Landing page `Sign In` button and use `Twitter` button to register                                                                                                                                                                                                           | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign in                                      | User able to sign in username and password                                                                                                                           | Click Landing page `Sign In` menu button or navbar `Sign In` menu button and enter credentials                                                                                                                                                                                     | User sign in                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign out                                     | User able to sign out and cannot access site content (expect `Help`)                                                                                                 | Click navbar `Sign Out` menu button and confirm sign out                                                                                                                                                                                                                           | User sign out                | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile                                      | User able to update profile including; bio, avatar and following categories                                                                                          | Click navbar `User -> Profile` menu button and update bio, avatar and following categories                                                                                                                                                                                         | User profile                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion creation                                  | User able to create opinion                                                                                                                                          | Click navbar `Opinion -> New` menu button or `Following Feed`/`Category Feed` `New Opinion` button, enter opinion details and save as `Draft`                                                                                                                                      | Opinion creation             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion creation                                  | A user's `Draft` opinions may be accessed only by that user                                                                                                          | Click navbar `Opinion -> Drafts` menu button                                                                                                                                                                                                                                       | Opinion creation             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion update                                    | A user can edit their opinions content                                                                                                                               | From any list of opinions, click the `Edit` icon on the opinion card to open the opinion in edit mode and update content                                                                                                                                                           | Opinion update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion update                                    | A user can update their opinion's status                                                                                                                             | Click navbar `Opinion -> Drafts` menu button, click the `Edit` icon on the opinion card, update opinion details and save as `Preview`                                                                                                                                              | Opinion update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion update                                    | A user can update their opinion's status                                                                                                                             | Click navbar `Opinion -> Previews` menu button, click the `Edit` icon on the opinion card, update opinion details and save as `Publish`                                                                                                                                            | Opinion update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Pre-publish status opinion only visible to author | User's can not view other user's opinion's which are in `Draft` or `Preview` status                                                                                  | Pre-publish status opinions from other users do not appear in any list of opinions                                                                                                                                                                                                 | Opinion list/view            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Published status opinions visible to all users    | User's can view other user's published opinion's                                                                                                                     | Click navbar `Opinion -> All` menu button, and click the `Read` icon on the opinion card                                                                                                                                                                                           | Opinion list/view            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion delete                                    | A user can delete their opinion's                                                                                                                                    | From any list of opinions, click the `Edit` icon on the opinion card to open the opinion in edit mode and click `Delete` to delete the opinion                                                                                                                                     | Content delete               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment creation (opinion)                        | A user can create a comment on another user's opinion                                                                                                                | From any list of opinions, click the `Read` icon on the opinion card to view the opinion and click the comment icon to create a comment                                                                                                                                            | Comment creation             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment viewable (opinion)                        | Comments created on an opinion may be viewed                                                                                                                         | From any list of opinions, click the `Read` icon on the opinion card to view the opinion and comments created on the opinion are viewable                                                                                                                                          | Comment view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment update (opinion)                          | User's may update their comments' content                                                                                                                            | From the Opinion page or any list of comments, click the `Edit` icon on the card for their comment to open the comment in edit mode and update content                                                                                                                             | Comment update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment pseudo delete (opinion)                   | User's may delete their comments' content (content is removed from database and comment placeholder maintains the structure of the comment tree)                     | From the Opinion page or any list of comments, click the `Edit` icon on the card for their comment to open the comment in edit mode and and click `Delete` to delete the comment content. Comment may not be opened in edit mode again.                                            | Comment update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment creation (comment)                        | A user can create a comment on another comment                                                                                                                       | From the Opinion page click the comment icon on a comment to create a comment                                                                                                                                                                                                      | Comment creation             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment viewable (comment)                        | Comments created on a comment may be viewed                                                                                                                          | From the Opinion page or any list of comments, click the `Read` icon on the comment card to view the comment and comments created on the comment are viewable                                                                                                                      | Comment view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment update (comment)                          | User's may update their comments' content                                                                                                                            | From the Opinion page or any list of comments, click the `Edit` icon on the card for their comment to open the comment in edit mode and update content                                                                                                                             | Comment update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment pseudo delete (comment)                   | User's may delete their comments' content (content is removed from database and comment placeholder maintains the structure of the comment tree)                     | From the Opinion page or any list of comments, click the `Edit` icon on the card for their comment to open the comment in edit mode and and click `Delete` to delete the comment content. Comment may not be opened in edit mode again.                                            | Comment update               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion/comment agree                             | A user can mark content as agree and the status will be reflected in display                                                                                         | From the reactions icons for any opinion/comment, click the `Agree` icon                                                                                                                                                                                                           | Opinion/comment view         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion/comment disagree                          | A user can mark content as disagree and the status will be reflected in display                                                                                      | From the reactions icons for any opinion/comment, click the `Disagree` icon                                                                                                                                                                                                        | Opinion/comment view         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion/comment hide                              | A user can mark content as hide and, opinions will not appear in their opinion list, and comment's contents will not be displayed                                    | From the reactions icons for any opinion/comment, click the `Hide` icon                                                                                                                                                                                                            | Opinion/comment view         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion/comment share                             | A user can get a copy of a link to share a specific opinion or comment                                                                                               | From the reactions icons for any opinion/comment, click the `Share` icon                                                                                                                                                                                                           | Opinion/comment share modal  | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion/comment report                            | A user can report opinion for comment for review by a moderator                                                                                                      | From the reactions icons for any opinion/comment, click the `Share` icon                                                                                                                                                                                                           | Opinion/comment report modal | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion pin/unpin                                 | A user can pin an opinion for easy access in the pinned list                                                                                                         | From any list of opinions, click the `Read` icon on the opinion card to view the opinion and click the `Pin` icon to pin an opinion or click the `Unpin` icon to unpin the opinion. Select the navbar `Opinion -> Pinned` menu button to se a list of all pinned opinions.         | Opinion view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion reviews                                   | A user view all their opinions which are in a review status                                                                                                          | Click navbar `Opinion -> Reviews` menu button, and click the `Read`/`Edit` icon on the opinion card to read/edit an opinion from the list of pending/under/unacceptable status opinions.                                                                                           | Opinion view/update          | ![pass](https://badgen.net/badge/checks/Pass/green) |
| New Followed author opinions                      | A user view all their opinions by authors they follow since their last login                                                                                         | Click navbar `Opinion -> New Followed Author Opinions` menu button, and click the `Read` icon on the opinion card to read an opinion from the list of new opinions. After signin out and in again, the list will be empty.                                                         | Opinion view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| All Followed author opinions                      | A user view all their opinions by authors they follow                                                                                                                | Click navbar `Opinion -> All Followed Author Opinions` menu button, and click the `Read` icon on the opinion card to read an opinion from the list of new opinions.                                                                                                                | Opinion view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Following feed                                    | A user view the feed of opinions by authors they follow                                                                                                              | Click navbar `Home` menu button, and click the `Following` icon on the `Feeds` panel.                                                                                                                                                                                              | Opinion view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Category feed                                     | A user view the feed of opinions from categories they follow (selected in their profile view)                                                                        | Click navbar `Home` menu button, and click the `Category` icon on the `Feeds` panel.                                                                                                                                                                                               | Opinion view                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion and Comment menu access                   | Only author group members can see and have access to Opinion and Comment menus                                                                                       | From any screen when logged in, select all options in the Opinion and Comment menus                                                                                                                                                                                                | All signed in pages          | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator menu access                             | Only moderator group members have access to the Moderator menu                                                                                                       | From any screen when logged in as a moderator, select all options in the Moderator menu. When logged in as an author, the menu is not available                                                                                                                                    | All signed in pages          | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Self-assign content pending review                | Moderator group members can self-assign content pending review so they can review it                                                                                 | From moderator menu click `Moderate -> Opinion Review Pending` or `Moderate -> Comment Review Pending`, click the `Review` icon on the opinion/comment card to open the content page in review mode, and click the `Assign` button to self-assign                                  | Opinion/comment review       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Submit content reviews                            | Moderator group members can submit a review finding on content under review. Acceptable content appear is public listings and, unacceptable content is not displayed | From moderator menu click `Moderate -> Opinion Review In Progress` or `Moderate -> Comment Review In Progress`, click the `Review` icon on the opinion/comment card to open the content page in review mode, enter review finding and click the `Acceptable`/`Unacceptable` button | Opinion/comment review       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| View content unacceptable content                 | Moderator group members can view content which a review has deemed to be unacceptable                                                                                | From moderator menu click `Moderate -> Opinion Review Unacceptable` or `Moderate -> Comment Review Unacceptable`, click the `Read`/`Review` icon on the opinion/comment card to open the content page                                                                              | Opinion/comment review       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Search                                            | A user can perform opinion searches using the search terms listed on the `Help` page from the search box in the navbar                                               | Enter search terms in the search box an click the `Search` button                                                                                                                                                                                                                  | Opinion search               | ![pass](https://badgen.net/badge/checks/Pass/green) |

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
