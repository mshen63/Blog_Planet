## Welcome to Emily and Michelle's Blog and Portfolio Page!

* This project contains three main pages: the blog page, Michelle's about page, and Emily's about page
* The blog posts are displayed in chronological order
* Anyone with the ~secret passcode~ can log in and write posts to our blog! As of now, only members of the Reliable Rhinos pod can provide their email to get the passcode emailed to them
* Logged in users will be able to write posts which they can choose to draft and come back to or publish to the blog
* Editor uses markdown and supports syntax highlighting and rich content embedding 
* On the top banner, you will see links that can lead to each of our personal pages where you can learn more about us

## Technologies Used
* Flask, HTML (Jinja), CSS (Sass)
* SQLite Peewee database for storing and querying our blog posts
* pygments to support syntax highlighting
* micawber to support Youtube video and other rich content embedding
* markdown to allow for greater creativity with blog posts

## Installation

Please have python and pip3 installed!


Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage


Create your very own .env file using env.sample as a template!

Start flask development server
```bash
$ set FLASK_ENV=development
$ flask run
```


## Contribution
* We are always open to suggestions or changes! 
* Just send over a pull request or a PM on discord, and we'll always take your suggestions into account!
