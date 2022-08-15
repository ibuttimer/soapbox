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

| Artifact                                       | Download and installation instructions               |
|------------------------------------------------|------------------------------------------------------|
| [git](https://git-scm.com/)                    | https://git-scm.com/downloads                        |
| [Python](https://www.python.org/)              | https://www.python.org/downloads/                    |

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

#### Python Setup
In the `soapbox` folder, run the following command to install the necessary python packages:
```shell
> pip install -r requirements-dev.txt
```
#### Production versus Development Setup
There are two requirements files:
* [requirements.txt](requirements.txt) which installs the production requirements, and
* [requirements-dev.txt](requirements-dev.txt) which installs extra development-only requirements in addition to the production requirements from [requirements.txt](requirements.txt) 
