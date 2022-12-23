- [Strategy](#strategy)
- [Scope](#scope)
  - [User Stories/Objectives](#user-storiesobjectives)
  - [Objectives Implementation](#objectives-implementation)
- [Structure](#structure)
- [Skeleton](#skeleton)
- [General layout](#general-layout)
- [Wireframes](#wireframes)
  - [Landing page](#landing-page)
  - [Signup page](#signup-page)
  - [Login page](#login-page)
  - [Home page](#home-page)
    - [Home page (Following)](#home-page-following)
    - [Home page (Category)](#home-page-category)
  - [Opinion page](#opinion-page)
  - [Opinion Read page](#opinion-read-page)
  - [Opinion Compose page](#opinion-compose-page)
  - [Opinion Preview page](#opinion-preview-page)
  - [Category page](#category-page)
  - [Moderator page](#moderator-page)
  - [Review page](#review-page)
  - [Profile page](#profile-page)
- [UX Surface](#ux-surface)
  - [Font](#font)
  - [Colour Scheme](#colour-scheme)
  - [UX Elements](#ux-elements)
  - [Accessibility](#accessibility)
- [Data](#data)
  - [Data Storage](#data-storage)
    - [Database schema](#database-schema)
  - [External Libraries](#external-libraries)
- [Errata](#errata)
  - [](#)

# Strategy
The strategy is to create a website allowing the user to post opinions and comment on opinions posted by other users.

The target audience for the application are people wishing to express opinions and engage in online debate.

# Scope
The scope of the project will be to allow the user to:
- Login and logout
- Depending on role, create and view or just view, opinions and comments
- Depending on role, like/unlike/report, opinions and comments
- Follow and unfollow other users
- Depending on role, delete previously created opinions

## User Stories/Objectives

### Agile methodology
An agile methodology will be used during the application development, using Google Projects as the agile tool.

The project artifacts are:
- [Soapbox Development](https://github.com/users/ibuttimer/projects/1)
- [Milestones](https://github.com/ibuttimer/soapbox/milestones)
- Project snapshots are available in the [agile](../../agile) folder and combined summary in [management_snapshots.pdf](../../agile/management_snapshots.pdf)

### User Stories
User Stores are logged in [GitHub Issues](https://github.com/ibuttimer/soapbox/issues?q=+label%3Auserstory+)

| Title                                                                                                              | Labels                               | Description                                                                                                                                                              |
|--------------------------------------------------------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Epic: Authorisation, authentication and permission features](https://github.com/ibuttimer/soapbox/issues/50)      | `kanban`, `epic`                     | Apply authorisation, authentication and permission features to application.                                                                                              |
| [Epic: Manage, query and manipulate opinions](https://github.com/ibuttimer/soapbox/issues/52)                      | `kanban`, `epic`                     | Implement a data model, application features and business logic to manage, query and manipulate opinion data in order to provide content for the application.            |
| [User Story: Login](https://github.com/ibuttimer/soapbox/issues/1)                                                 | `userstory`, `kanban`                | As a **user**, I can **login**, so that **I can access the site**.                                                                                                       |
| [User Story: Register user](https://github.com/ibuttimer/soapbox/issues/2)                                         | `userstory`, `kanban`                | As a **user**, I can **register**, so that **I can access the site**.                                                                                                    |
| [User Story: Create opinion](https://github.com/ibuttimer/soapbox/issues/3)                                        | `userstory`, `kanban`                | As a **verified user**, I can **create an opinion**, so that **other users may view it**.                                                                                |
| [User Story: View an opinion](https://github.com/ibuttimer/soapbox/issues/4)                                       | `userstory`, `kanban`                | As **any user**, I can **view an opinion**, so that **I can read it**.                                                                                                   |
| [User Story: Login with social media](https://github.com/ibuttimer/soapbox/issues/5)                               | `userstory`, `kanban`                | As a **user**, I can **login with social media**, so that **I can access the site**.                                                                                     |
| [User Story: Add opinion comment](https://github.com/ibuttimer/soapbox/issues/6)                                   | `userstory`, `kanban`                | As a **verified user**, I can **add a comment to another user's posted opinion**, so that **I can express my opinion**.                                                  |
| [User Story: Add opinion agree/disagree/hide](https://github.com/ibuttimer/soapbox/issues/7)                       | `userstory`, `kanban`                | As a **verified user**, I can **mark a comment as agree/disagree/hide**, so that **opinions that users agreement level with an opinions can be highlighted**.            |
| [User Story: Logout](https://github.com/ibuttimer/soapbox/issues/9)                                                | `userstory`, `kanban`                | As a **user**, I can **logout**, so that **I can no longer access protected areas of the site**.                                                                         |
| [User Story: Follow a user](https://github.com/ibuttimer/soapbox/issues/10)                                        | `userstory`, `kanban`                | As a **user**, I can **follow another user**, so that **I receive a notification when they post a new opinion**.                                                         |
| [User Story: Unfollow a user](https://github.com/ibuttimer/soapbox/issues/11)                                      | `userstory`, `kanban`                | As a **user**, I can **unfollow another user**, so that **I do not receive notifications when they post a new opinion**.                                                 |
| [User Story: Delete an opinion](https://github.com/ibuttimer/soapbox/issues/12)                                    | `userstory`, `kanban`                | As a **verified user**, I can **delete an opinion I previously created**, so that **I can manage my list of opinions**.                                                  |
| [User Story: Pin opinion](https://github.com/ibuttimer/soapbox/issues/13)                                          | `userstory`, `kanban`                | As a **verified user**, I can **pin an opinion I previously created**, so that **it appears in my list of pinned opinions**.                                             |
| [User Story: Unpin opinion](https://github.com/ibuttimer/soapbox/issues/14)                                        | `userstory`, `kanban`                | As a **verified user**, I can **unpin an opinion I previously pinned**, so that **it no longer appears in my list of pinned opinions**.                                  |
| [User Story: Paginated list of opinions](https://github.com/ibuttimer/soapbox/issues/19)                           | `userstory`, `kanban`                | As a **user**, I can **view a paginated list of opinions**, so that **I can control the number of opinions viewed at a time**.                                           |
| [User Story: Like opinion](https://github.com/ibuttimer/soapbox/issues/20)                                         | `userstory`, `kanban`                | As a **verified user**, I can **like an opinion**, so that **I can provide feedback to the author**.                                                                     |
| [User Story: Unlike opinion](https://github.com/ibuttimer/soapbox/issues/21)                                       | `userstory`, `kanban`                | As a **verified user**, I can **unlike an opinion**, so that **I can manage the list of opinions marked as liked**.                                                      |
| [User Story: Add comment comment](https://github.com/ibuttimer/soapbox/issues/22)                                  | `userstory`, `kanban`                | As a **verified user**, I can **add a comment to another user's posted comment **, so that **I can express my opinion**.                                                 |
| [User Story: Report opinion/comment](https://github.com/ibuttimer/soapbox/issues/23)                               | `userstory`, `kanban`                | As a **verified user**, I can **report an opinion/comment**, so that **it may be reviewed by a moderator for objectionable content**.                                    |
| [User Story: Approve/block opinions/comments](https://github.com/ibuttimer/soapbox/issues/24)                      | `userstory`, `kanban`                | As a **moderator**, I can **approve/block opinions/comments that have been reported**, so that **I can prevent objectionable content from being displayed on the site**. |
| [User Story: Search](https://github.com/ibuttimer/soapbox/issues/25)                                               | `userstory`, `kanban`                | As a **verified user**, I can **search for opinions**, so that **I can read opinions related to the search terms I specify**.                                            |
| [User Story: Profile](https://github.com/ibuttimer/soapbox/issues/26)                                              | `userstory`, `kanban`                | As a **verified user**, I can **update my profile**, so that **I can provide other users with information about myself**.                                                |
| [User Story: Edit opinion](https://github.com/ibuttimer/soapbox/issues/38)                                         | `userstory`, `kanban`                | As a **verified user**, I can **edit my opinions**, so that **I can update the content**.                                                                                |
| [User Story: Preview opinion](https://github.com/ibuttimer/soapbox/issues/39)                                      | `userstory`, `kanban`                | As a **verified user**, I can **preview my opinions while creating/editing**, so that **I can check how the content looks**.                                             |
| [User Story: List options](https://github.com/ibuttimer/soapbox/issues/44)                                         | `userstory`, `kanban`                | As a **verified user**, I can **list opinions**, so that **I can select and read an opinion**.                                                                           |
| [User Story: Notification of changes made to opinions](https://github.com/ibuttimer/soapbox/issues/51)             | `userstory`, `kanban`                | As a **verified user**, I **receive notification of changes made to my opinions**, so that **I know when a moderator review of my opinions has been completed**.         |
| [User Story: Hide opinions](https://github.com/ibuttimer/soapbox/issues/57)                                        | `userstory`, `kanban`                | As a **verified user**, I can **hide an opinion**, so that **it is no longer displayed when viewing all opinions**.                                                      |
| [User Story: Unhide opinion](https://github.com/ibuttimer/soapbox/issues/58)                                       | `userstory`, `kanban`                | As a **verified user**, I can **unhide an opinion**, so that **it is displayed when viewing all opinions**.                                                              |
| [User Story: Share opinion/comment](https://github.com/ibuttimer/soapbox/issues/60)                                | `userstory`, `kanban`                | As a **verified user**, I can **share an opinion/comment**, so that **I can provide a link to easily access the opinion/comment**.                                       |
| [User Story: Like/unlike comment](https://github.com/ibuttimer/soapbox/issues/63)                                  | `userstory`, `kanban`                | As a **verified user**, I can **like/unlike a comment**, so that **I can manage the list of comments marked as liked**.                                                  |
| [User Story: Hide/unhide comment](https://github.com/ibuttimer/soapbox/issues/64)                                  | `userstory`, `kanban`                | As a **verified user**, I can **hide/unhide a comment**, so that **I can manage the list of comments marked as hidden**.                                                 |
| [User Story: Agree/disagree comment](https://github.com/ibuttimer/soapbox/issues/65)                               | `userstory`, `kanban`                | As a **verified user**, I can **agree/disagree with a comment**, so that **I can manage the list of comments marked as agree/disagree**.                                 |
| [User Story: Delete comment](https://github.com/ibuttimer/soapbox/issues/69)                                       | `userstory`, `kanban`                | As a **verified user**, I can **delete a comment I previously created**, so that **I can manage my list of comments**.                                                   |
| [User Story: Edit comments](https://github.com/ibuttimer/soapbox/issues/73)                                        | `userstory`, `kanban`                | As a **verified user**, I can **edit my comments**, so that **I can correct/add content**.                                                                               |
| [User Story: Home page](https://github.com/ibuttimer/soapbox/issues/76)                                            | `userstory`, `kanban`                | As a **verified user**, I can **view the home page**, so that **I can view my category feed and my following feed**.                                                     |
| [User Story: Admin can assign users to groups](https://github.com/ibuttimer/soapbox/issues/77)                     | `userstory`, `kanban`                | As a **site administrator**, I can **assign user's to groups**, so that **they have appropriated permissions for their roles**.                                          |

## Objectives Implementation

| Title                                                                                                              |                                                                 Implementation                                                                 |
|--------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------:|
| [Epic: Authorisation, authentication and permission features](https://github.com/ibuttimer/soapbox/issues/50)      | See [User registration and authentication](../../README.md#user-registration-and-authentication) and [User roles](../../README.md#user-roles)  |
| [User Story: Login](https://github.com/ibuttimer/soapbox/issues/1)                                                 |                                                                       "                                                                        |
| [User Story: Register user](https://github.com/ibuttimer/soapbox/issues/2)                                         |                                                                       "                                                                        |
| [User Story: Login with social media](https://github.com/ibuttimer/soapbox/issues/5)                               |                                                                       "                                                                        |
| [User Story: Logout](https://github.com/ibuttimer/soapbox/issues/9)                                                |                                                                       "                                                                        |
| [User Story: Profile](https://github.com/ibuttimer/soapbox/issues/26)                                              |                                                                       "                                                                        |
| [User Story: Admin can assign users to groups](https://github.com/ibuttimer/soapbox/issues/77)                     |                                                                       "                                                                        |


| Title                                                                                                              |                         Implementation                         |
|--------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------:|
| [Epic: Manage, query and manipulate opinions](https://github.com/ibuttimer/soapbox/issues/52)                      |        See [Content CRUD](../../README.md#content-crud)        |
| [User Story: Create opinion](https://github.com/ibuttimer/soapbox/issues/3)                                        |                               "                                |
| [User Story: View an opinion](https://github.com/ibuttimer/soapbox/issues/4)                                       |                               "                                |
| [User Story: Add opinion comment](https://github.com/ibuttimer/soapbox/issues/6)                                   |                               "                                |
| [User Story: Add comment comment](https://github.com/ibuttimer/soapbox/issues/22)                                  |                               "                                |
| [User Story: Edit opinion](https://github.com/ibuttimer/soapbox/issues/38)                                         |                               "                                |
| [User Story: Preview opinion](https://github.com/ibuttimer/soapbox/issues/39)                                      |                               "                                |
| [User Story: Delete comment](https://github.com/ibuttimer/soapbox/issues/69)                                       |                               "                                |
| [User Story: Edit comments](https://github.com/ibuttimer/soapbox/issues/73)                                        |                               "                                |
| [User Story: Add opinion agree/disagree/hide](https://github.com/ibuttimer/soapbox/issues/7)                       | See [Content interaction](../../README.md#content-interaction) |
| [User Story: Follow a user](https://github.com/ibuttimer/soapbox/issues/10)                                        |                               "                                |
| [User Story: Unfollow a user](https://github.com/ibuttimer/soapbox/issues/11)                                      |                               "                                |
| [User Story: Delete an opinion](https://github.com/ibuttimer/soapbox/issues/12)                                    |                               "                                |
| [User Story: Pin opinion](https://github.com/ibuttimer/soapbox/issues/13)                                          |                               "                                |
| [User Story: Unpin opinion](https://github.com/ibuttimer/soapbox/issues/14)                                        |                               "                                |
| [User Story: Like opinion](https://github.com/ibuttimer/soapbox/issues/20)                                         |                               "                                |
| [User Story: Unlike opinion](https://github.com/ibuttimer/soapbox/issues/21)                                       |                               "                                |
| [User Story: Report opinion/comment](https://github.com/ibuttimer/soapbox/issues/23)                               |                               "                                |
| [User Story: Hide opinions](https://github.com/ibuttimer/soapbox/issues/57)                                        |                               "                                |
| [User Story: Unhide opinion](https://github.com/ibuttimer/soapbox/issues/58)                                       |                               "                                |
| [User Story: Share opinion/comment](https://github.com/ibuttimer/soapbox/issues/60)                                |                               "                                |
| [User Story: Like/unlike comment](https://github.com/ibuttimer/soapbox/issues/63)                                  |                               "                                |
| [User Story: Hide/unhide comment](https://github.com/ibuttimer/soapbox/issues/64)                                  |                               "                                |
| [User Story: Agree/disagree comment](https://github.com/ibuttimer/soapbox/issues/65)                               |                               "                                |
| [User Story: Home page](https://github.com/ibuttimer/soapbox/issues/76)                                            |       See [Opinion feeds](../../README.md#opinion-feeds)       |
| [User Story: Paginated list of opinions](https://github.com/ibuttimer/soapbox/issues/19)                           |                               "                                |
| [User Story: List options](https://github.com/ibuttimer/soapbox/issues/44)                                         |                               "                                |
| [User Story: Search](https://github.com/ibuttimer/soapbox/issues/25)                                               |      See [Content search](../../README.md#content-search)      |
| [User Story: Notification of changes made to opinions](https://github.com/ibuttimer/soapbox/issues/51)             |  See [User notifications](../../README.md#user-notifications)  |
| [User Story: Approve/block opinions/comments](https://github.com/ibuttimer/soapbox/issues/24)                      |            See [Moderate](../../README.md#moderate)            |

# Structure
As there separate functionality will be required for users with different roles, the website will utilise a tree navigation structure.

# Skeleton
The website will consist of the following pages:

| Page            | Description                                                                                                 |
|-----------------|-------------------------------------------------------------------------------------------------------------|
| Landing         | The landing page will allow users to log in or register.                                                    |
| Home            | The home page will display the user's opinion feed, and provide shortcuts to frequently used functionality. |
| Opinion         | The opinion page will provide access to all opinion-related functionality.                                  |
| Opinion Read    | The opinion read page will allow users to view and comment on opinions.                                     |
| Opinion Compose | The opinion compose page will allow users to compose opinions.                                              |
| Opinion Preview | The opinion preview page will allow users to preview the appearance of draft opinions.                      |
| Category        | The opinion page will provide access to all category-related functionality.                                 |
| Moderator       | The moderator page will provide access to all moderator-related functionality.                              |
| Review          | The review page will allow moderators to approve or reject opinions submitted for review                    |
| Profile         | The profile page will display a user's profile and allow users to edit their own profile.                   |

# General layout

Each of the pages will have the same general layout:

- A menu at top of page, with current page highlighted in a different colour.
  The buttons will contain the appropriate text, and icons will be used to visually represent the function of each page.
- A footer at bottom of page will provide general site related information.

# Wireframes
Wireframes of page layouts are as followings:

## Landing page

The Landing page will have the following features:
- The option for users to login or register

| Large screen                        | Small screen                       |
|-------------------------------------|------------------------------------|
| ![](img/soapbox-landing-large.png)  | ![](img/soapbox-landing-small.png) |

## Signup page

| Large screen                      | Small screen                      |
|-----------------------------------|-----------------------------------|
| ![](img/soapbox-signup-large.png) | ![](img/soapbox-signup-small.png) |

## Login page

| Large screen                     | Small screen                     |
|----------------------------------|----------------------------------|
| ![](img/soapbox-login-large.png) | ![](img/soapbox-login-small.png) |

## Home page

The Home page will have the following features:
- Display the user's opinion feed, and provide shortcuts to frequently used functionality.

### Home page (Following)

| Large screen                               | Small screen                              |
|--------------------------------------------|-------------------------------------------|
| ![](img/soapbox-main-following-large.png)  | ![](img/soapbox-main-following-small.png) |

### Home page (Category)

| Large screen                             | Small screen                             |
|------------------------------------------|------------------------------------------|
| ![](img/soapbox-main-category-large.png) | ![](img/soapbox-main-category-small.png) |

## Opinion page

The Opinion page will have the following features:
- Allow access to all opinion functionality.

| Large screen                         | Small screen                       |
|--------------------------------------|------------------------------------|
| ![](img/soapbox-opinion-large.png)   | ![](img/soapbox-opinion-small.png) |

## Opinion Read page

The Opinion Read page will have the following features:
- Allow users to view and comment on opinions.

| Large screen                      | Small screen                    |
|-----------------------------------|---------------------------------|
| ![](img/soapbox-read-large.png)   | ![](img/soapbox-read-small.png) |

## Opinion Compose page

The Opinion Compose page will have the following features:
- Allow users to compose opinions.

| Large screen                        | Small screen                       |
|-------------------------------------|------------------------------------|
| ![](img/soapbox-compose-large.png)  | ![](img/soapbox-compose-small.png) |

## Opinion Preview page

The Opinion Preview page will have the following features:
- Allow users to preview the appearance of draft opinions.

| Large screen                       | Small screen                       |
|------------------------------------|------------------------------------|
| ![](img/soapbox-preview-large.png) | ![](img/soapbox-preview-small.png) |

## Category page

The Category page will have the following features:
- Allow users to access to all category-related functionality.

| Large screen                          | Small screen                        |
|---------------------------------------|-------------------------------------|
| ![](img/soapbox-category-large.png)   | ![](img/soapbox-category-small.png) |

## Moderator page

The Moderator page will have the following features:
- Allow users to access to all moderator-related functionality.

| Large screen                          | Small screen                        |
|---------------------------------------|-------------------------------------|
| ![](img/soapbox-moderate-large.png)   | ![](img/soapbox-moderate-small.png) |

## Review page

The Review page will have the following features:
- Allow moderators to approve or reject opinions submitted for review.

| Large screen                      | Small screen                      |
|-----------------------------------|-----------------------------------|
| ![](img/soapbox-review-large.png) | ![](img/soapbox-review-small.png) |

## Profile page

The Profile page will have the following features:
- Allow users to view another user's profile and edit their own profile

| Large screen                         | Small screen                       |
|--------------------------------------|------------------------------------|
| ![](img/soapbox-profile-large.png)   | ![](img/soapbox-profile-small.png) |



# UX Surface
## Font
The font used for title text will be [Rubik](https://fonts.google.com/specimen/Rubik?preview.text=SoapBox%20-%20where%20opinions%20matter&preview.text_type=custom) from Google fonts.
The font used for paragraph text will be [Barlow Condensed](https://fonts.google.com/specimen/Barlow+Condensed?preview.text=SoapBox%20-%20where%20opinions%20matter&preview.text_type=custom) from Google fonts.

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=Rubik:ital,wght@0,400;0,700;1,400;1,700&display=swap');

font-family: 'Barlow Condensed', sans-serif;
font-family: 'Rubik', sans-serif;
```

## Colour Scheme

Colour scheme courtesy of [Huemint](https://huemint.com/bootstrap-basic/#palette=f3fafa-ffffff-00032d-1c4858-E0E0E0-b5a7af) with updates 
from [Adobe Color Accessibility Tools](https://color.adobe.com/create/color-contrast-analyzer) improve contrast.

## UX Elements

No custom UX elements will be utilised, as the [Bootstrap](https://getbootstrap.com/) library provides all required elements.

## Accessibility
The guidelines outlined in the following will be followed:

- [W3C - Using ARIA](https://www.w3.org/TR/using-aria/)
- [TPGi - Short note on aria-label, aria-labelledby, and aria-describedby](https://www.tpgi.com/short-note-on-aria-label-aria-labelledby-and-aria-describedby/)


# Data
## Data Storage
Data will be stored in a [PostgreSQL](https://www.postgresql.org/) database.

### Database schema
The database schema will consist of several tables:

| Name               | Description                                  |
|--------------------|----------------------------------------------|
 | user               | site users                                   |
 | opinions           | user generated opinions                      |
 | categories         | categories to which opinions may be assigned |
 | comments           | user comments                                |
 | statuses           | statuses which may be assigned to opinions   |
 | follow status      | user's author following records              |
 | agreement status   | user's agree/disagree records                |
 | hide status        | user's content hide records                  |
 | pin status         | user's pinned opinion records                |
 | user categories    | user's following category records            |
 | opinion categories | opinion's assigned category records          |
 | reviews            | opinion reviews                              |

[![](img/soapbox-database-schema.png)]

## External Libraries
The following third party libraries will be utilised:

| Library                                                                                              | Use                                                                                                               | Description                                                                                                                                                                                                                               |
|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [django](https://pypi.org/project/psycopg2/)                                                         | Application framework                                                                                             | Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.                                                                                                                                |
| [psycopg2](https://pypi.org/project/psycopg2/)                                                       | Access PostgreSQL database                                                                                        | This library provides a complete implementation of the Python DB API 2.0 specification. It was designed for heavily multi-threaded applications that create and destroy lots of cursors.                                                  |
| [django-environ](https://pypi.org/project/django-environ/)                                           | Application configuration                                                                                         | Configuration of Django application with environment variables.                                                                                                                                                                           |
| [dj3-cloudinary-storage](https://pypi.org/project/dj3-cloudinary-storage/)                           | Cloudinary storages for both media and static files                                                               | Django Cloudinary Storage is a Django package that facilitates integration with Cloudinary by implementing the [Django Storage API](https://docs.djangoproject.com/en/4.1/howto/custom-file-storage/).                                    |
| [django-summernote](https://pypi.org/project/django-summernote/)                                     | HTML text editor                                                                                                  | Make the [Summernote](https://github.com/summernote/summernote) WYSIWYG editor available to the Django admin site and Forms.                                                                                                              |
| [gunicorn](https://pypi.org/project/gunicorn/)                                                       | Serve application on Heroku                                                                                       | WSGI HTTP Server for UNIX                                                                                                                                                                                                                 |
| [django-allauth](https://pypi.org/project/django-allauth/)                                           | User authentication and registration                                                                              | Integrated set of Django applications addressing authentication, registration, account management as well as 3rd party (social) account authentication.                                                                                   |
| [Bootstrap](https://getbootstrap.com/)                                                               | Frontend page styling                                                                                             | A powerful, extensible, and feature-packed frontend toolkit to build fast, responsive sites. See [Get started with Bootstrap](https://getbootstrap.com/docs/5.2/getting-started/introduction/).                                           |
| [Font Awesome](https://github.com/FortAwesome/Font-Awesome)                                          | Frontend icons                                                                                                    | A powerful, extensible, and feature-packed frontend toolkit to build fast, responsive sites. See [Get started with Bootstrap](https://getbootstrap.com/docs/5.2/getting-started/introduction/).                                           |
| _The following libraries will be used during development_                                            |                                                                                                                   |                                                                                                                                                                                                                                           |
| [pycodestyle](https://pypi.org/project/pycodestyle/)                                                 | [PEP8](http://www.python.org/dev/peps/pep-0008/) compliance check                                                 | Python style guide checker                                                                                                                                                                                                                |
| [coverage](https://pypi.org/project/pycodestyle/)                                                    | Code coverage testing                                                                                             | Measures code coverage, typically during test execution. It uses the code analysis tools and tracing hooks provided in the Python standard library to determine which lines are executable, and which have been executed.                 |
| [Pillow](https://pypi.org/project/Pillow/)                                                           | Image validation (required by [ImageField](https://docs.djangoproject.com/en/4.1/ref/models/fields/#imagefield))  | Imaging Library                                                                                                                                                                                                                           |
| [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)<br>[lxml](https://pypi.org/project/lxml/) | Capture HTML page content                                                                                         | A library that makes it easy to scrape information from web pages. For details see the [documentation](https://www.crummy.com/software/BeautifulSoup/).<br>XML processing library. For details see the [documentation](https://lxml.de/). |



# Errata
## 