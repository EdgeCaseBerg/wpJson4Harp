wpJson4Harp
===========

Author: Ethan J. Eldridge  
Website: ejehardenberg.github.io  

Python tool to migrate WP contents to JSON for use in [harp](http://harpjs.com/)


Current Features:

1. Creates JSON for Posts
2. Creates JSON for Comments

To Run:

    Fill out the database credentials at the top of the file
    $python wp2json4harp.py > _data.json

And then profit. All data is printed to stdout so you can just pipe it to a file
if you want, support for writing to a file might come later on.
