wpJson4Harp
===========

Author: Ethan J. Eldridge  
Website: ejehardenberg.github.io  

Python tool to migrate WP contents to JSON for use in [harp](http://harpjs.com/)


Current Features:

1. Creates JSON for Posts
2. Creates JSON for Comments
3. Creates JSON for Nav
4. Creates JSON for Pages

To Run:

    Fill out the database credentials at the top of the file
    $python wp2json4harp.py 
    You'll now have an example.jade file, and a few directories with _data.json inside.

Once you've ran the script, you'll get folders for each of the _data.json files. This makes things a bit easier to coordinate, and you can see from the example jade file how you can access the information pulled from your blog.

Some configuration details:

Configuration is at the top of the script, you'll need to enter your database credentials and if you only want to include published posts, set the `ONLY_PUBLISHED` variable to True. If you have a strange encoding on your database, specify it in the ENCODING constant.

TODO: 

- Better slugs for url pulled for nav?
- Use getopt to make cmd line arguments instead of constants
- More examples!


