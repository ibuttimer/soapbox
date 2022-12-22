# SoapBox

In the tradition of soapbox orators at Speakers' Corner in Hyde Park in London, 
SoapBox is a community platform that allows users to post opinions and engage in online discussions.
Depending on a users' role they may post opinions and comment on other's opinions, or simply view opinions and comment. 

The site is aimed at people seeking a platform in which to express opinions and engage in debate.

###### Fig 1: Responsive Mockup
![Responsive Mockup](doc/media/responsive.png)

Section links
- [Features](#features)
- [Design](#design)
- [Development](#development-and-local-deployment)
- [Test](#test)
- [Cloud-based Deployment](#cloud-based-deployment)
- [Credits](#credits)

## Features 

### Existing Features
#### Common Features

##### Navigation Bar
The fully responsive navigation bar provides access to the content pages (`Opinion`/`Comment`) and `Moderator` pages, and `User` menu. The current page is highlighted for easy identification and users can easily navigate to the other pages.

###### Fig 2: Navigation Bar
![Nav Bar](doc/media/nav-bar-images.png)

### User registration and authentication
Users may register for an account or alternatively use OAuth to sign in via their Google or Twitter accounts.

###### Fig 3: User registration and authentication
|               User registration                |             User authentication              |
|:----------------------------------------------:|:--------------------------------------------:|
| ![User register/login](doc/media/register.png) | ![User register/login](doc/media/signin.png) | 

### User roles
There are three user roles:
- Author

    Authors may create and read content. This is the default role for new users.

- Moderator

    Moderators have the same abilities as Authors and in addition are responsible for reviewing content which has been reported by other users.

- Site administrator

  The site administrator may perform all functions on the site, including assigning Moderators.

### User notifications
Users receive notifications following sign in. These include a new user notification, content changes notification

###### Fig 4: User notifications
|                       New user notification                       |                   Login notification                    |
|:-----------------------------------------------------------------:|:-------------------------------------------------------:|
|   ![New user notification](doc/media/notification-new-user.png)   | ![Login notification](doc/media/notification-login.png) | 
|                          **New content**                          |                                                         |
| ![New user notification](doc/media/notification-new-content.png)  |                                                         | 

### Content CRUD
#### Content creation
Users may create and publish opinions, comments on opinions and comments on comments.
#### Content view
All users may view opinions and their associated comments.
#### Content edit
Authors may edit their opinions and comments.
#### Content delete
Authors may delete their opinions, resulting in the opinion and associated comments being deleted.
Comment's may be pseudo deleted, i.e. the comment will be marked as deleted and it's contents deleted the content. A comment placeholder will remain to ensure the comment tree structure.

###### Fig 5: Content CRUD
|                  Create opinion                   |                      Create comment                       |
|:-------------------------------------------------:|:---------------------------------------------------------:|
| ![Opinion creation](doc/media/create-opinion.png) | ![Comment creation](doc/media/create-opinion-comment.png) | 
|                 **Opinion view**                  |                     **Comment view**                      |
|    ![Opinion view](doc/media/view-opinion.png)    |    ![Comment view](doc/media/multi-level-comments.png)    | 
|                 **Opinion edit**                  |                     **Comment edit**                      |
|    ![Opinion edit](doc/media/edit-opinion.png)    |        ![Comment edit](doc/media/edit-comment.png)        | 
|                **Opinion delete**                 |                    **Comment delete**                     |
|  ![Opinion delete](doc/media/delete-opinion.png)  |      ![Comment delete](doc/media/delete-comment.png)      | 

### Content interaction
Users may interact with content via the reactions bar, allowing them to:
- mark content as agree/disagree
- follow content authors to receive notifications of new opinions they create
- pin opinions for easy retrieval vis the `Opinion -> Pinned` listing
- share content via short urls
- hide opinions, so they don't appear in opinion listings and, hide comment's content
- report content to be reviewed by a moderator
- comment pseudo delete, see [Content delete](#content-delete)
- edit their own comments

###### Fig 6: Content interaction
|              Agree opinion/comment              |              Disagree opinion/comment               |
|:-----------------------------------------------:|:---------------------------------------------------:|
|  ![Agree opinion/comment](doc/media/agree.png)  | ![Disagree opinion/comment](doc/media/disagree.png) | 
|           **Follow content authors**            |                   **Pin opinion**                   |
|      ![Hide opinion](doc/media/follow.png)      |         ![Hide comment](doc/media/pin.png)          | 
|                **Hide opinion**                 |                  **Hide comment**                   |
|   ![Hide opinion](doc/media/hide-opinion.png)   |     ![Hide comment](doc/media/hide-comment.png)     | 
|               **Report opinion**                |                 **Report comment**                  |
| ![Report opinion](doc/media/report-opinion.png) |   ![Report comment](doc/media/report-comment.png)   | 
|               **Delete comment**                |                  **Edit comment**                   |
| See [Fig 5: Content CRUD](#fig-5-content-crud)  |   See [Fig 5: Content CRUD](#fig-5-content-crud)    | 

### Content search
Users may search for opinions via search box in the navbar at the top of the screen.
Please see [Advanced Search](https://soapbox-opinions.herokuapp.com/help/#advanced-search-help) for full list of search terms.

###### Fig 6: Content search
|                    Search opinion by author                    |                       Search opinion by author and title                        |
|:--------------------------------------------------------------:|:-------------------------------------------------------------------------------:|
| ![Search opinion by author](doc/media/search-opinion-user.png) | ![Search opinion by author and title](doc/media/search-opinion-user-title.png)  | 

### Opinion feeds
There are two opinion feeds available to the user on the home page:
- Following

  A feed of opinion from authors which the user is following.

- Category

  A feed of opinions from categories which the user has selected to follow in their profile.


###### Fig 7: Opinion feeds
|                 Following feed                  |                 Category feed                 |              All feed               |
|:-----------------------------------------------:|:---------------------------------------------:|:-----------------------------------:|
| ![Following feed](doc/media/following-feed.png) | ![Category feed](doc/media/category-feed.png) | ![All feed](doc/media/all-feed.png) | 


### Moderate
Moderators have access to the moderator menu which allows them to:
- Self-assign content (opinions/comments) pending review
- Submit a review finding on content under review

  Acceptable content will appear in public listings and, unacceptable content is not displayed.

- View content unacceptable content

###### Fig 8: Moderate
|                      Pending review                      |                        Under review                        |                        Unacceptable                         |
|:--------------------------------------------------------:|:----------------------------------------------------------:|:-----------------------------------------------------------:|
| ![Pending review](doc/media/moderate-review-pending.png) | ![Under review](doc/media/moderate-review-in-progress.png) | ![Unacceptable](doc/media/moderate-review-unacceptable.png) | 


### Future enhancements
- Add user listing and search capabilities
- Add comment search
- Add advanced search page

## Design
The design specification is available in [design.md](doc/design/design.md).

## Development and Local Deployment
### Environment
The development environment requires:

| Artifact                                 | Download and installation instructions               |
|------------------------------------------|------------------------------------------------------|
| [Node.js](https://nodejs.org/)           | https://nodejs.org/en/download/                      |
| [npm](https://www.npmjs.com/)            | Included with Node.js installation                   |
| [git](https://git-scm.com/)              | https://git-scm.com/downloads                        |
| [Python](https://www.python.org/)        | https://www.python.org/downloads/                    |
| [Django](https://www.djangoproject.com/) | https://www.djangoproject.com/download/              |

### Setup
#### Clone Repository
In an appropriate folder, run the following commands:
```shell
> git clone https://github.com/ibuttimer/soapbox.git
> cd soapbox
```
Alternatively, most IDEs provide an option to create a project from Version Control. 

#### Virtual Environment
It is recommended that a virtual environment be used for development purposes.
Please see [Creating a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) for details.

> __Note:__ Make sure to [activate the virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

#### Environment Setup
In a terminal window, in the `soapbox` folder, run the following command to setup required environment artifacts:
```shell
> npm install
```

#### Python Setup
In the `soapbox` folder, run the following command to install the necessary python packages:
```shell
> pip install -r requirements-dev.txt
```
##### Production versus Development Setup
There are two requirements files:
* [requirements.txt](requirements.txt) which installs the production requirements, and
* [requirements-dev.txt](requirements-dev.txt) which installs extra development-only requirements in addition to the production requirements from [requirements.txt](requirements.txt) 

###### Table 1: Configuration settings
| Key                      | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ENV_FILE                 | If using an environment file, specifies the file to use. Defaults to `.env` in the project root folder.                                                                                                                                                                                                                                                                                                                                                                                 |
| PORT                     | Port application is served on; default 8000                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| DEBUG                    | A boolean that turns on/off debug mode; set to any of 'true', 'on', 'ok', 'y', 'yes', '1' to enable                                                                                                                                                                                                                                                                                                                                                                                     |
| DEVELOPMENT              | A boolean that turns on/off development mode; set to any of 'true', 'on', 'ok', 'y', 'yes', '1' to enable                                                                                                                                                                                                                                                                                                                                                                               |
| TEST                     | A boolean that turns on/off test mode; set to any of 'true', 'on', 'ok', 'y', 'yes', '1' to enable. Only valid when development mode is enabled.                                                                                                                                                                                                                                                                                                                                        |
| SECRET_KEY               | [Secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SECRET_KEY) for a particular Django installation. See [Secret Key Generation](#secret-key-generation)                                                                                                                                                                                                                                                                                                      |
| DATABASE_URL             | [Database url](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)                                                                                                                                                                                                                                                                                                                                                                                                           |
| CLOUDINARY_URL           | [Cloudinary url](https://pypi.org/project/dj3-cloudinary-storage/)                                                                                                                                                                                                                                                                                                                                                                                                                      |
| AVATAR_BLANK_URL         | Url of [blank avatar](static/img/avatar_blank.svg)                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| SITE_ID                  | Id (primary key) of site in the `django_site` table of the database. See [Configure authentication](#configure-authentication).                                                                                                                                                                                                                                                                                                                                                         |
| HEROKU_HOSTNAME          | [Hostname](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts) of application on Heroku.<br>__Note:__ To specify multiple hosts, use a comma-separated list with no spaces.<br>__Note:__ Set to `localhost,127.0.0.1` in local development mode                                                                                                                                                                                                                          |
| REMOTE_DATABASE_URL      | Url of remote PostgreSQL database resource.<br>For a Heroku app with a [Heroku Postgres](https://elements.heroku.com/addons/heroku-postgresql) addon this is available from `DATABASE_URL` in the app `Settings -> Config Vars`.<br>For an [ElephantSQL](https://www.elephantsql.com/) database this is available from `URL` in the instance details.<br>__Note:__ Only required for admin purposes, see database configuration under [Cloud-based Deployment](#cloud-based-deployment) |
| GOOGLE_SITE_VERIFICATION | [Google Search Console](https://search.google.com/search-console) meta tag verification value for [site ownership verification](https://support.google.com/webmasters/answer/9008080?hl=en)                                                                                                                                                                                                                                                                                             |


#### Environment variables
Set environment variables corresponding to the keys in [Table 1: Configuration settings](#table-1-configuration-settings).

E.g.
```shell
For Linux and Mac:                       For Windows:
$ export DEVELOPMENT=true                > set DEVELOPMENT=true
```

##### Secret Key Generation
A convenient method of generating a secret key is to run the following command and copy its output.

```shell
$ python -c "import secrets; print(secrets.token_urlsafe())"
```

#### Social Account Login
In order to configure social account login, the following actions must be performed.

##### Google
The Google provider is [OAuth2](https://developers.google.com/identity/protocols/OAuth2) based, 
and a Google app is needed to obtain a key and secret through the [Google Developer Console](https://console.developers.google.com/).

- Login to the [Google Developer Console](https://console.developers.google.com/)
- Click on the `Select a project` button and then select `New Project`
* Give the project a name and click `Create`
* Once created click `Select Project` on the notification or select the project from the `Select a project` modal
* From the sidebar menu select [APIs & Services -> Credentials](https://console.cloud.google.com/apis/credentials)
* Select `CREATE CREDENTIALS` and `OAuth client ID` from the dropdown as the type of credential
* Select `Web application` as the application type, and specify a `Name`
* Add the site domain name or test domain name in `Authorized JavaScript origins`
* Add the `http://127.0.0.1:8000/accounts/google/login/callback/` in `Authorised redirect URIs`
* Select `CREATE`
* From the `OAuth client created` modal, copy the `Client ID` and `Client Secret` or download the information in JSON format.
* From the sidebar menu select `APIs & Services -> OAuth consent screen`
* Provide the following App information
  * App name
  * User support email
  * App logo
* Under `Authorised domains` add the site domain
* Add an email address for `Developer contact information`
* Select `SAVE AND CONTINUE`
* Under `Authorised domains`, select `ADD OR REMOVE SCOPES` and check the boxes for `.../auth/userinfo.email` and `.../auth/userinfo.profile` 
* Select `SAVE AND CONTINUE`
* Under `Test users`, add the email address for the Google accounts to be used in testing
* Select `SAVE AND CONTINUE`

##### Twitter
* Login to Twitter and signup to the [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
* Create a new app and save the Consumer Keys: `API Key`, `API Key Secret` and `Bearer Token`
* Open the app in the dashboard and under `User authentication settings`, select `Set up`
* Select `Web App, Automated App or Bot` for `Type of App`
* Under `App info`, set
  * `Callback URI / Redirect URL` to `http://127.0.0.1:8000/accounts/twitter/login/callback/`
  * `Website URL` to the Heroku app URL, e.g. [https://soapbox-opinions.herokuapp.com/](https://soapbox-opinions.herokuapp.com//)
  * `Organization name` to `SoapBox`
* Select `Save`, and copy the OAuth 2.0 Client ID and Client Secret displayed, and store securely.
* Select `Done`
* It is necessary to [apply for Elevated access](https://developer.twitter.com/en/portal/products/elevated) to the Twitter API, in order to access to private resources.
  Without Elevated access it is not possible to use Twitter as a sign in provider


### Before first run
Before running the application for the first time following cloning from the repository and setting up a new database,
the following steps must be performed, from a terminal window, in the `soapbox` folder.

#### Initialise the database
````shell
$ python manage.py migrate
````
#### Create a superuser
Enter `Username`, `Password` and optionally `Email address`.
````shell
$ python manage.py createsuperuser
````
#### Build Bootstrap
Build a customised version of Bootstrap.
````shell
$ npm run build
````

#### Configure authentication
From [Configure authentication](https://django-allauth.readthedocs.io/en/latest/installation.html#post-installation)
- Add a Site for your domain in the database
  - Login to `http://&lt;domain&gt;/admin/sites/site/` as the previously created superuser, e.g. http://127.0.0.1:8000/admin/sites/site/ 
  - Add a Site for your domain (django.contrib.sites app).
      
    E.g.

    | Domain name    | Display name   |
    |----------------|----------------| 
    | 127.0.0.1:8000 | my domain      | 

    __Note:__ The id (primary key) of the site must be added to the application configuration. See `SITE_ID` in [Table 1: Configuration settings](#table-1-configuration-settings).

- For each OAuth based provider, add a SocialApp in `http://&lt;domain&gt;/admin/socialaccount/socialapp/`, 
  e.g. http://127.0.0.1:8000/admin/socialaccount/socialapp/, containing the required client credentials
        
  - Google
    [django-allauth Google provider info](https://django-allauth.readthedocs.io/en/latest/providers.html#google)

    | Provider | Name   | Client id                                        | Secret key                                        | 
    |----------|--------|---------------------------------------------------|--------------------------------------------------| 
    | google   | Google | `client_id` from the OAuth 2.0 Client credentials | `client_secret` from the OAuth 2.0 Client credentials | 

    And add the Site for your domain to the `Chosen sites` list

  - Twitter
    [django-allauth Twitter provider info](https://django-allauth.readthedocs.io/en/latest/providers.html#twitter) 

    | Provider | Name    | Client id                                         | Secret key                                        | 
    |---------|----------|---------------------------------------------------|--------------------------------------------------| 
    | twitter  | Twitter | `API Key` from the Consumer Keys | `API Key Secret` from the Consumer Keys | 

    And add the Site for your domain to the `Chosen sites` list

### Application structure
The application structure is as follows:

```
├─ README.md            - this file
├─ agile                - project management
├─ doc                  - documentation
│  ├─ design            - design related documentation
│  └─ test              - test reports
├─ manage.py            - application entry point
├─ soapbox              - main Django application
├─ base                 - base Django application
├─ categories           - categories Django application
├─ django_tests         - Django Test Tools test scripts
├─ jest_tests           - Jest javascript tests
├─ opinions             - opinions Django application
├─ user                 - user Django application
├─ staticfiles          - static files
│  ├─ css               - custom CSS
│  ├─ img               - images
│  └─ js                - custom JavaScript
├─ templates            - application templates
├─ tests                - unittest test scripts
└─ utils                - utility function scripts
```

## Cloud-based Deployment

The site was deployed on [Heroku](https://www.heroku.com).

### Heroku CLI
Optionally, the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) may be used to update the application on Heroku.
With the Heroku CLI installed, in a terminal window, in the `soapbox` folder:
- Log in to your Heroku account and follow the prompts to create a new SSH public key.

  ```shell
  $ heroku login
  ```

### Deployment
The following steps were followed to deploy the website:
- Login to Heroku in a browser
- From the dashboard select `New -> Create new app`
- Set the value for `App name`, choose the appropriate region and click `Create app`
- To provision the application with a database, a [Heroku Postgres](https://elements.heroku.com/addons/heroku-postgresql) database or alternative, such as an [ElephantSQL](https://www.elephantsql.com/) database may be utilised.
  - For [Heroku Postgres](https://elements.heroku.com/addons/heroku-postgresql), from the app settings, select the `Resources` tab.
      - Under `Add-ons` add the following
          1. `Heroku Postgres` - PostgreSQL [database as a service](https://elements.heroku.com/addons/heroku-postgresql)
  - For [ElephantSQL](https://www.elephantsql.com/) database, follow the `Create a new instance` instructions under the `Getting started` section of the [ElephantSQL documentation](https://www.elephantsql.com/docs/index.html).
- From the app settings, select the `Resources` tab.
    - Under `Add-ons` add the following
      1. `Cloudinary - Image and Video Management` - [Cloudinary Image & Video Tools](https://elements.heroku.com/addons/cloudinary)

            __Note:__ In order the access the dashboard for the provisioned Cloudinary account, use the [Heroku CLI](https://devcenter.heroku.com/articles/cloudinary#management-console)
            ```shell
            $ heroku addons:open cloudinary
            ```

- From the app settings, select the `Settings` tab.
    - Under `Buildpacks` add the following buildpacks
        1. `heroku/python`
    - Under `Config Vars` add the following environment variables

        | Key                      | Value                                                                                                                                                                             |
        |-------------------|---------------------------------------------------------------------------------------------------------------------------------|
        | PORT                     | 8000                                                                                                                                                                              |
        | SECRET_KEY               | [Secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SECRET_KEY) for a particular Django installation                                                     |
        | HEROKU_HOSTNAME          | [Hostname](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts) of application on Heroku                                                                            |
        | AVATAR_BLANK_URL         | Url of [blank avatar](static/img/avatar_blank.svg)                                                                                                                                |
        | SITE_ID                  | Id (primary key) of site in the `django_site` table of the database. See [Configure authentication](#configure-authentication).                                                   |
        |                          | _The following keys are automatically added when `Resources` are provisioned:_                                                                                                   |
        | CLOUDINARY_URL           | [Cloudinary url](https://pypi.org/project/dj3-cloudinary-storage/)                                                                                                                |
        | GOOGLE_SITE_VERIFICATION | [Google Search Console](https://search.google.com/search-console) meta tag verification value for [site ownership verification](https://support.google.com/webmasters/answer/9008080?hl=en) |

    - Add the `DATABASE_URL` environment variable under `Config Vars`, if required

      | Key               | Value                                                                                                                                                                                                                                                                                 |
      |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
      | DATABASE_URL      | [Database url](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)<br>- [Heroku Postgres](https://elements.heroku.com/addons/heroku-postgresql) database, automatically added when `Resources` are provisioned<br>- [ElephantSQL](https://www.elephantsql.com/) database, copy the `URL` from the instance details page |


See [Table 1: Configuration settings](#table-1-configuration-settings) for details.

If any other settings vary from the defaults outlined in [Table 1: Configuration settings](#table-1-configuration-settings) they must be added as well.

- From the app settings, select the `Deploy` tab.
    - For the `Deployment method`, select `GitHub` and link the Heroku app to the GitHub repository.

      __Note:__ To configure GitHub integration, you have to authenticate with GitHub. You only have to do this once per Heroku account. See [GitHub Integration (Heroku GitHub Deploys)](https://devcenter.heroku.com/articles/github-integration).
    - `Enable Automatic Deploys` under `Automatic deploys` to enable automatic deploys from GitHub following a GitHub push if desired.
    - The application may also be deployed manually using `Deploy Branch` under `Manual deploy`
    - Alternatively, the application may be deployed via the [Heroku CLI](#heroku-cli).
      After logging into the Heroku CLI in a terminal window, in the `soapbox` folder:
        - Check the list of `git` remotes

          ```shell
          $ git remote -v
          origin  https://github.com/ibuttimer/soapbox.git (fetch)
          origin  https://github.com/ibuttimer/soapbox.git (push)
          ```

      - If there is no `git` remotes for `heroku` listed, add one 

          ```shell
          $ git remote add heroku https://git.heroku.com/soapbox-opinions.git

          $ git remote -v       
          heroku  https://git.heroku.com/soapbox-opinions.git (fetch)
          heroku  https://git.heroku.com/soapbox-opinions.git (push)
          origin  https://github.com/ibuttimer/soapbox.git (fetch)
          origin  https://github.com/ibuttimer/soapbox.git (push)
          ```

      - After committing change locally, push to Heroku

          ```shell
          $ git push heroku main
          ```

- Initialise the database and Create a superuser 

    Involves the same procedure as outlined in [Initialise the database](#initialise-the-database) and [Create a superuser](#create-a-superuser)
    but may be run from the local machine. 
    - From a [Development/Local Deployment](#developmentlocal-deployment) 
      - Initialise the database
        ````shell
        $ python manage.py migrate --database=remote
        ````
      - Create a superuser

        Enter `Username`, `Password` and optionally `Email address`.
        ````shell
        $ python manage.py createsuperuser --database=remote
        ````

      __Note:__ Ensure to specify the `--database=remote` option to apply the change to the database specified by the `REMOTE_DATABASE_URL` environment variable.

  - Alternatively, the [Heroku CLI](#heroku-cli) may be utilised.

    After logging into the Heroku CLI in a terminal window, in the `soapbox` folder:
      - Initialise the database
        ````shell
        $  heroku run python manage.py migrate --app soapbox-opinions
        ````
      - Create a superuser

        Enter `Username`, `Password` and optionally `Email address`.
        ````shell
        $ heroku run python manage.py createsuperuser --app soapbox-opinions
        ````
- Configure authentication

   Follow the same procedure as outlined in [Configure authentication](#configure-authentication) using the 
   Heroku domain as `&lt;domain&gt;`, e.g. `soapbox-opinions.herokuapp.com` 

The live website is available at [https://soapbox-opinions.herokuapp.com/](https://soapbox-opinions.herokuapp.com//)

## Test
The tests information and results are available in [test.md](doc/test/test.md).



## Credits

The following resources were used to build the website.

### Content

- Logo [bullhorn image](https://github.com/FortAwesome/Font-Awesome/blob/6.x/svgs/solid/bullhorn.svg), [Icons License](https://github.com/FortAwesome/Font-Awesome#license) [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), by [Font Awesome](https://fontawesome.com/)
- The favicon for the site was generated by [RealFaviconGenerator](https://realfavicongenerator.net/) from [bullhorn image](https://github.com/FortAwesome/Font-Awesome/blob/6.x/svgs/solid/bullhorn.svg) , [Icons License](https://github.com/FortAwesome/Font-Awesome#license) [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), by [Font Awesome](https://fontawesome.com/)
- Avatars courtesy of [AV̇ȦTARMAKER](https://avatarmaker.com/)
- [Blank avatar image](static/img/avatar_blank.svg) by [WingTillDie](https://pixabay.com/users/wingtilldie-3058071/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1577909) from [Pixabay](https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1577909)
- Landing page [bullhorn image](static/img/free-speech-6249234_1280.png) by [Gordon Johnson](https://pixabay.com/users/gdj-1086657/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=6249234") from [Pixabay](https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=6249234)
- [Speech balloons image](static/img/balloons-1187260_1280.png) by [Sabine Kroschel](https://pixabay.com/users/pixaline-1569622/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1187260) from [Pixabay](https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1187260), opacity modified
- [No speak monkey image](static/img/no-speak-monkey-148893.png) by [OpenClipart-Vectors](https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=148893) from [Pixabay](https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=148893), cropped
- The [Responsive Mockup](#fig-1-responsive-mockup) image was generated courtesy of [Website Mockup Generator](https://websitemockupgenerator.com/)

### Code

- [Secret Key Generation](#secret-key-generation) courtesy of [Humberto Rocha](https://humberto.io/blog/tldr-generate-django-secret-key/)
- [Social Account Login](#social-account-login) and [Configure authentication](#configure-authentication) details courtesy of
  [django-allauth](https://django-allauth.readthedocs.io/en/latest/overview.html) and [Geoffrey Mungai](https://www.section.io/engineering-education/django-google-oauth/)
 