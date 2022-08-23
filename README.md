# SoapBox

In the tradition of soapbox orators at Speakers' Corner in Hyde Park in London, 
SoapBox is a community platform that allows users to post opinions and engage in online discussions.
Depending on a users' role they may post opinions and comment on other's opinions, or simply view opinions and comment. 

The site is aimed at people seeking a platform in which to express opinions and engage in debate.

## Features 


## Design
The design specification is available in [design.md](doc/design/design.md).

## Development/Local Deployment
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
In the `soapbox` folder, run the following command to setup required environment artifacts:
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
| Key                      | Value                                                                                                                                                                              |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PORT                     | Port application is served on; default 8000                                                                                                                                        |
| DEBUG                    | A boolean that turns on/off debug mode; set to any of 'true', 'on', 'ok', 'y', 'yes', '1' to enable                                                                                |
| DEVELOPMENT              | A boolean that turns on/off development mode; set to any of 'true', 'on', 'ok', 'y', 'yes', '1' to enable                                                                          |
| SECRET_KEY               | [Secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SECRET_KEY) for a particular Django installation. See [Secret Key Generation](#secret-key-generation) |
| DATABASE_URL             | [Database url](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)                                                                                                      |
| CLOUDINARY_URL           | [Cloudinary url](https://pypi.org/project/dj3-cloudinary-storage/)                                                                                                                 |
| HEROKU_HOSTNAME          | [Hostname](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts) of application on Heroku<br>__Note:__ Not required in local development mode                         |

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



### Application structure
The application structure is as follows:

```
├─ README.md            - this file
├─ doc                  - documentation
│  ├─ design            - design related documentation
│  └─ test              - test reports
├─ manage.py            - application entry point
├─ soapbox              - main Django application
├─ base                 - base Django application
├─ static               - static file
│  ├─ css               - custom CSS
│  ├─ img               - images
│  └─ js                - custom JavaScript
└─ tests                - test scripts
```

## Cloud-based Deployment

The site was deployed on [Heroku](https://www.heroku.com).

The following steps were followed to deploy the website:
- Login to Heroku
- From the dashboard select `New -> Create new app`
- Set the value for `App name`, choose the appropriate region and click `Create app`
- From the app settings, select the `Resources` tab.
    - Under `Add-ons` add the following
        1. `Heroku Postgres` - PostgreSQL [database as a service](https://elements.heroku.com/addons/heroku-postgresql)
        2. `Cloudinary - Image and Video Management` - [Cloudinary Image & Video Tools](https://elements.heroku.com/addons/cloudinary)
- From the app settings, select the `Settings` tab.
    - Under `Buildpacks` add the following buildpacks
        1. `heroku/python`
    - Under `Config Vars` add the following environment variables

        | Key             | Value                                                                                                                         |
        |-----------------|-------------------------------------------------------------------------------------------------------------------------------|
        | PORT            | 8000                                                                                                                          |
        | SECRET_KEY      | [Secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SECRET_KEY) for a particular Django installation |
        | HEROKU_HOSTNAME | [Hostname](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts) of application on Heroku                        |
        |                 | The following keys are automatically added when `Resources` are provisioned                                                   |
        | DATABASE_URL    | [Database url](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)                                                 |
        | CLOUDINARY_URL  | [Cloudinary url](https://pypi.org/project/dj3-cloudinary-storage/)                                                            |

        See [Table 1: Configuration settings](#table-1-configuration-settings) for details.

        If any other settings vary from the defaults outlined in [Table 1: Configuration settings](#table-1-configuration-settings) they must be added as well.

- From the app settings, select the `Deploy` tab.
    - For the `Deployment method`, select `GitHub` and link the Heroku app to the GitHub repository.

      __Note:__ To configure GitHub integration, you have to authenticate with GitHub. You only have to do this once per Heroku account. See [GitHub Integration (Heroku GitHub Deploys)](https://devcenter.heroku.com/articles/github-integration).
    - `Enable Automatic Deploys` under `Automatic deploys` to enable automatic deploys from GitHub following a GitHub push if desired.
    - The application may also be deployed manually using `Deploy Branch` under `Manual deploy`

The live website is available at [https://soapbox-opinions.herokuapp.com/](https://soapbox-opinions.herokuapp.com//)




## Credits

The following resources were used to build the website.

### Content

- The favicon for the site *will be* generated by [RealFaviconGenerator](https://realfavicongenerator.net/) from [graph image](https://lineicons.com/icons/?search=graph&type=free) by [Lineicons](https://lineicons.com/)

### Code

- [Secret Key Generation](#secret-key-generation) courtesy of [Humberto Rocha](https://humberto.io/blog/tldr-generate-django-secret-key/)
