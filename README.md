# Least Degrees Between Actors
=======================
Graph Setup
------------
To run the program, an API key from TMDB must first be obtained. After getting the key and storing it in a Python file with the name of `tmdb_api_key.py` and a single variable in the file called `api_key` with its value being the string of the API key.

To initialize the NetworkX graph, create a new graph and then force an update to build a base foundation of connections by running the `actorgraph.py` file.
```
Would you like to open an existing NetworkX graph? (y/n): n
ARE YOU SURE YOU WANT TO CREATE A NEW GRAPH?
This will OVERWRITE any previous graph.
Confirm (y/n): y
Would you like to update the graph? (y/n): y
ARE YOU SURE YOU WANT TO UPDATE?
This process will take an extended amount of time.
Confirm (y/n): y
```
This process will take an extended period of time, but will lead to a fuller graph. This will also display multiple messages in the terminal to see the progress of the training for each actor added to the NetworkX graph.

Alternatively, two actors can be entered which will force an update of the graph automatically. This could potentially take longer as it exponentially increases degrees of connections with each iteration that a connection is not found.

Finding Connections
-----------------
Run the actorgraph.py and choose any two actors to connect
```
Would you like to open an existing NetworkX graph? (y/n): y
Would you like to update the graph? (y/n): n
Enter the first actor: Charlie Chaplin
Enter the second actor: Brad Pitt
```
This will find the shortest path between the actors based on the data in the model. This may not be the shortest path ever if certain actors or movies weren't fed into the model, but the training process should minimize this situation.
```
Charlie Chaplin
['Modern Times', 'The Great Dictator']
Harry Wilson
['The Cincinnati Kid']
Michael Greene
['Less Than Zero']
Brad Pitt
```
Charlie Chaplin is in *Modern Times* and *The Great Dictator* with Harry Wilson, who is in *The Cincinnati Kid* with Michael Greene, who is finally in *Less Than Zero* with Brad Pitt. Four of those roles are actually "uncredited" to the actors, but the data is stored in TMDB so a path is still there to connect them.

Each time an actor is entered the model fetches from TMDB to update the actors' connections to increase the chance of a shorter path being found either now or in the future.