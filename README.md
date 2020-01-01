# Equimolar-Blog
This is a flask blogging engine for publishing articles. A live extended implementation will be made available at [Equimolar.com](http://Equimolar.com). In 
In this ReadMe we will be going through the following content  
1. [The Problem](#-the-problem)
2. [Existing python-blog repos](#-why-not-fork-one-of-the-python-blog-repos)
2. [This Solution](#-the-solution:)
4. [How to Use](#-how-to-use)

## The Problem:
I wanted to build a blog for publishing articles and some python programmes, thus, I may have a hard time using wordpress, which sounds like the simplest, in conjunction with my python codes. Why not fork one of the python-blog repos?
After trying out alot of them, read more in the next section, none of them seems to solve my needs as stated below.

The needs that call for the development of the app, is listed below. Obviously, if this are not the features you needed, you may simply jump to the next section to see other available options built by some brilliant people, in fact there are alot out there you can pick from, so feel free to explore alot of brilliant options out there depending on your needs.
### List of the requirements
1. Support Postings by Many Users.
2. Article should support tagging
3. Articles must be editable even after publishing
4. One must be able to put posts in draft untill published
5. Allow assigning of multiple rigths to the blog posters: In general, I need three rights.
    * Authour: Users will be able to write an article and edit only their articles
    * Editor: Anyone given this right will be able to create a new article, and edit all posts, even if it does not belong to them
    * Registrar: Will be able to add new users, assign rigths, and edit users details.  
    *Note: Users can be given multiple roles*
6. Posts should be written in markdown and I must be able to preview in real-time while editing. That is, I should be able open preview windows side-by-side with the markdown text-box.
7. Articles must be searchable.
8. Display related articles to the current article being read.
9. Extendable for use in existing applications: Thus shhould be cotained in a blueprint to make things easy to whoever wants to port it into another application
10. Must be able to host some light-weight files, which may be linked to from in the blog posts


## Why not fork one of the python-blog repos 
There are currently a gazillion number of already available python blog frameworks like, Flask-Blog, Flask-Blogging, Simple-Flask-Blog, and Weblog, which are all brilliant, but based on my needs, there is no single that ever address all my problems. For example, after trying out several of them, I short listed two, which were Flask-Bloogging and Weblog.  
* Flask-Blogging is highly sophisticated and provides alot of functionalities out of the box, but the down-sides, in my own applications will be: dirty url(which I have raised an Issue ticket for), and 2. currently, It does not support search functionalities (though this issue has been raised by the owner). At first, I believe Flask-Blogging is the only option I had but its complex structure makes tweeking a relatively long process task for a 'beginner' like me.  
* Weblog is very simple Flask blog application, it lacks a whole lot of features out of the box, but its simplicity makes it highly customizable, but the major drawback is that it only support posting opf articles by sending a post request to the publish end-point. Again, having to add a whole lot a functionalities makes one look as if one is build an entirely new programe.

## The Solution:
Equimolar-Blog was built based on the knowledge gained by trying out several of the programmes discussed earlier, just that they were modified to suit [the needs](#-List-of-the-requirements).
Equimolar-Blog is Flask blog solution that solves all the previously stated requirements using the simplest method possible. 
dependent upon a list of several publicly available codes:
1. Flask-WTF : Form the forms
2. Flask-Sqlalchemy : Provided an ORM based database
3. Flask-Whoosh3 : Provides the search fuctionality
4. Flask-Security : Makes handling of accesses a deadly simple task
5. Flask-Upload : Used to handle the file upload process
6. Flask-Admin : For managing the database from the front-end
7. Bootstrap4 : To make the website look gorgeous without stress.

## How to Use
___
### Starting up
#### Test mode:

1. cd into the folder, on windows something like
    >C:\Users\Ewetoye Ibrahim>> `cd C:\path to the folder\Equimolar-Blog`

2. [Optional] Create a virtual environment and activate it
3. Install the requirement file: `python -m pip install requirement.txt`
4. [Optional] If you have change the database to something else other than sqlite3 configured, you should first make sure that the database exist, even if blank. But it is well-known that this is not required for sqlite3 databases as it will be created on the fly if not found at the specified location
5. Setup the database. something like:
    >C:\path to the folder\Equimolar-Blog>> `python create_db.py`

    *Note: this should only be done on a test database; Never run this on procuction database!!!*

    The step creates all the tables in the model; create the three rights (Authour, Editor, and Registrar); adds four dummy users:

    <table>
        <thead>
            <th>Username</th>
            <th>Email</th>
            <th>Password</th>
            <th>Rigth(s)</th>
        </thead>
        <tbody>
            <tr>
                <td>Authour User</td>
                <td>authour@example.com</td>
                <td>password</td>
                <td>Authour</td>
            </tr>
            <tr>
                <td>Editor User</td>
                <td>editor@example.com</td>
                <td>password</td>
                <td>Editor</td>
            </tr>
            <tr>
                <td>Registrar User</td>
                <td>registrar@example.com</td>
                <td>password</td>
                <td>Registrar</td>
            </tr>
            <tr>
                <td>Owner User</td>
                <td>owner@example.com</td>
                <td>password</td>
                <td>Authour, Editor, Registrar</td>
            </tr>
        </tbody>
    </table>
    As such, the create_db.py file should be run on a production database, as it will create the afore-mentioned usersin the database.

6. Start the app from the command prompt: `python run.py`
    Now, your blog should be live at 127.0.0.1:5000

    
#### Production mode:

set the environment variable type into run.py directly:
1. Set the env variable:  
`set CONFIG_NAME=production`  
`set FLASK_APP=run.py`  
`flask run`

2. hardcode directly into run.py:  
Open run.py  
Edit the third line  
    >app = create_app(os.getenv('CONFIG_NAME', default='default'))

    to  
    >app = create_app('production')
* do `python run.py`

### Creating an article
Visit /writter endpoint. e.g `localhost:5000/writter`

### Editing an article
Visit the article, if you are either the one who posted the article or you have an Editor rigth, you will get to see an edit button at the top of article, click it and edit as needed.

Released: 1/1/2020 by [Ewetoye, Ibrahim](https://EwetoyeIbrahim.github.io)

