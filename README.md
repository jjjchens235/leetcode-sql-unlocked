
I'm not sure how to delegate the question_elements() method. There are a few moving pieces here that make it complicated. Firstly, question elements is needed by the question class, so should we let question class handle it.

#Option 1
We let questions class handle question_elements. That means we have to pass in a driver class and a hist_log class. Not a good idea.

#Option 2
Let's say  web_handler class is the one that gets question_elements. But we save question_elements to log class.
And from log class, we pass this in to questions class.


