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
5. Creates .md files for the Posts
6. Creates .md files for the pages

To Run:

    Fill out the database credentials at the top of the file
    $python wp2json4harp.py 
    You'll now have an example.jade file, and a few directories with _data.json inside.

Once you've ran the script, you'll get folders for each of the _data.json files. This makes things a bit easier to coordinate, and you can see from the example jade file how you can access the information pulled from your blog.

Some configuration details:

Configuration is at the top of the script, you'll need to enter your database credentials.
Optionally, you can fully configure the script using the constants below:

Configuration of Script
------------------------------------------------------------

<table>
	<thead>
		<tr>
			<th>Constant</th><th>What it does</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>MYSQL_HOST</td>
			<td>Defines the host of the database to connect to.</td>
		</tr>
		<tr>
			<td>MYSQL_USER</td>
			<td>Defines the user to connect to the database as</td>
		</tr>
		<tr>
			<td>MYSQL_PASS</td>
			<td>Defines the password to the database</td>
		</tr>
		<tr>
			<td>MYSQL_DB</td>
			<td>Defines the database name connected to on the host.</td>
		</tr>
		<tr>
			<td>WP_PREFIX</td>
			<td>The prefix to your wordpress tables, typically this is `wp_`</td>
		</tr>
		<tr>
			<td>ONLY_PUBLISHED</td>
			<td>Only retrieve posts and pages that have been published</td>
		</tr>
		<tr>
			<td>GENERATE_PAGES</td>
			<td>Generate a markdown file for the pages being pulled from the WP database. This will exist in the PAGES_DIR</td>
		</tr>
		<tr>
			<td>GENERATE_POSTS</td>
			<td>Generate a markdown file for the posts being pulled from the WP database. This will exist in the BLOG_DIR</td>
		</tr>
		<tr>
			<td>ROOT_DIR</td>
			<td>Where to generate all the files this script creates, leave empty by default for the area where the script is being ran</td>
		</tr>
		<tr>
			<td>ENCODING</td>
			<td>The encoding to decode the content from the database in, I've defaulted it to latin to handle some annoying unicode errors</td>
		</tr>
		<tr>
			<td>PAGES_DIR</td>
			<td>The directory name where the pages will be stored</td>
		</tr>
		<tr>
			<td>BLOG_DIR</td>
			<td>The directory name where the blog posts will be stored</td>
		</tr>
		<tr>
			<td>NAV_DIR</td>
			<td>The directory where the navigation json will be stored</td>
		</tr>
		<tr>
			<td>COMMENTS_DIR</td>
			<td>The directory where comments will be stored. </td>
		</tr>
		<tr>
			<td>EXAMPLE_FILE</td>
			<td>The name of the file that will be generated to show some of the posts and pages.</td>
		</tr>
	</tbody>
</table>

TODO: 

- Taxonomy?
- How does one pull in the comments to a post?
- Use getopt to make cmd line arguments instead of constants
- More examples!


