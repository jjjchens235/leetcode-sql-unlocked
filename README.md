
#Issue One

I'm not sure how to delegate the question_elements() method. There are a few moving pieces here that make it complicated. Firstly, question elements is needed by the question class, so should we let question class handle it.

#Option 1
We let questions class handle question_elements. That means we have to pass in a driver class and a hist_log class. Not a good idea.

#Option 2
Let's say  web_handler class is the one that gets question_elements. But we save question_elements to log class.
And from log class, we pass this in to questions class.


So since Option 2 is better, where do we start ?

Let's first move question elements to the web_driver class.
Let's then update leetcode_sql_unlocked.py

The logic in leetcocde_unlocked.py, lets call it main(), is that we create a HistLog object. The HistLog object then calls a method called is_stale_questions()





	
#Issue two - creating and reading in log question status

For q_elements log, we want to refresh from web if the last time we pulled was more than 13 days ago.
Or, if the elements log doesn't exist.
Else we just read in the last log

For q_state, this is where I'm stuck. HEre are the possiblities:
1. 

#Issue 3

If the table only has one column, we want to create a second column called 'ignore' filled with _ values

If first line has only two +, or two | then it is 1 column
if line is column name (not always on second lne), we count how much of that line doesnt match (|)


Actually ... forgot all of the above.
Let's do it like this.
We test what kind of table it is, there are 2, its first line either starts with 
Ok let's first assume we know it's either Table Type 1 (+) or Type 2 (|--) and we already have everything parsed into individual tables.
I think we can just append pre-made column to any table that only has one column


#Issue 4

Let's start from here before tackling issue 3. We first want to figure out what kind of table it is after we get table_lines
Table Type 1: They include + signs
Table Type 2: Don't include + signs. Instead, their second row is always |----|

For table type 1, we already solved this probelm.
For Table Typen 2, I think we have to append each line until we either get to a |--- in which case, we pop twice, add popped to temp table first_two, and then taking non-popped elements we create our first table.


#Issue 5
what happens if it's a new valid question, but it hasn't been uploaded to JP yet. In faxt let's expand this question a little more broadly, let's say there's a question that is valid that makes us error out, let's say we can't scrape it correctly.

How do we allow the user to try a new problem

We can solve it on the level of the method within web_handler.py, or within leetcode's main()

if solving at the level of web_handler methods, we would bewould need to find the methods where it would be ok to error out on.
