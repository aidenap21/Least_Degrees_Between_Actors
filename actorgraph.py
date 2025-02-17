import tmdbsimple as tmdb
import networkx as nx
import pickle
import requests
from training_actors import actors_by_decade
from tmdb_api_key import api_key

class ActorGraph:
    def __init__(self):
        tmdb.API_KEY = api_key
        tmdb.REQUESTS_TIMEOUT = (5, 5)  # seconds, for connect and read specifically 
        tmdb.REQUESTS_SESSION = requests.Session()
        
        self._graph = None

        while self._graph is None:
            existing = input("Would you like to open an existing NetworkX graph? (y/n): ")
            if existing.lower() == 'y':
                self._graph = pickle.load(open("tmdb_graph.pickle", "rb"))
                self._added_movies = pickle.load(open("checked_movies.pickle", "rb"))
            else:
                print("ARE YOU SURE YOU WANT TO CREATE A NEW GRAPH?\nThis will OVERWRITE any previous graph.")
                reset = input("Confirm (y/n): ")
                if reset.lower() == 'y':
                    self._graph = nx.Graph()
                    self._added_movies = {126314} # Manually adds this movie ID to blacklist since it contains only archive footage
        
        self._actors_by_decade = actors_by_decade

    def _add_movie_connection(self, actor1, actor2, movie):
        # Check if the edge already exists
        if self._graph.has_edge(actor1, actor2):
            # Append to the existing movie list
            self._graph[actor1][actor2]["movies"].add(movie)
        else:
            # Create a new edge with a list containing the movie
            self._graph.add_edge(actor1, actor2, movies=set([movie]))

    def force_update(self, decades=(1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020)):
        print("ARE YOU SURE YOU WANT TO UPDATE?\nThis process will take an extended amount of time.")
        confirm = input("Confirm (y/n): ")
        if confirm.lower() != 'y':
            print("Upgrade cancelled, exiting...")
            return

        movies_data = tmdb.Movies()
        movie_dict = dict()

        print(f"Initial number of nodes and edges and movie set size: {self._graph.number_of_nodes()} and {self._graph.number_of_edges()} and {len(self._added_movies)}")
        
        for movie in movies_data.popular()['results']:
            if movie['id'] in movie_dict or movie['id'] in self._added_movies:
                continue

            self._added_movies.add(movie['id'])

            movie_item = tmdb.Movies(movie['id'])
            movie_item.info()

            if {'id': 99, 'name': 'Documentary'} in movie_item.genres:
                continue

            movie_dict[movie['id']] = set([actor['id'] for actor in movie_item.credits()['cast']])

        # Add nodes and edges
        for movie, actors in movie_dict.items():
            for actor in actors:
                for co_actor in actors:
                    self._add_movie_connection(actor, co_actor, movie)
                    pickle.dump(self._graph, open("tmdb_graph.pickle", "wb"))
                    pickle.dump(self._added_movies, open("checked_movies.pickle", "wb"))

        # Force update from all decades passed in
        for decade in decades:
            for actor in self._actors_by_decade[str(decade) + "s"]:
                self._update_actor(actor)
        
        pickle.dump(self._graph, open("tmdb_graph.pickle", "wb"))
        pickle.dump(self._added_movies, open("checked_movies.pickle", "wb"))


        # Takes in 2 lists of movie IDs to update the graph
    def _update_actor(self, actor):
        print(f"BEFORE: {actor} number of nodes and edges and movie set size: {self._graph.number_of_nodes()} and {self._graph.number_of_edges()} and {len(self._added_movies)}")
        
        try:
            search = tmdb.Search()
            search.person(query=actor)
            actor_item = tmdb.People(search.results[0]['id'])
        except:
            print(f"ERROR WITH ACTOR: {actor}")
            return

        actor_item.info()

        movie_ids = set([movie['id'] for movie in actor_item.movie_credits()['cast']])
        movie_dict = dict()

        # Find the cast of every movie
        for movie in movie_ids:
            if movie in movie_dict or movie in self._added_movies:
                continue

            try:
                movie_item = tmdb.Movies(movie)
                movie_item.info()
            except:
                print(f"ERROR WITH MOVIE ID: {movie}")
                continue

            self._added_movies.add(movie)

            if {'id': 99, 'name': 'Documentary'} in movie_item.genres:
                continue
            
            movie_dict[movie] = set([actor['id'] for actor in movie_item.credits()['cast']])

        actor_set = set()

        # Add nodes and edges
        for movie, actors in movie_dict.items():
            actor_set.update(set(actors))
            for actor in actors:
                for co_actor in actors:
                    self._add_movie_connection(actor, co_actor, movie)

        pickle.dump(self._graph, open("tmdb_graph.pickle", "wb"))
        pickle.dump(self._added_movies, open("checked_movies.pickle", "wb"))
        print(f"AFTER {actor} number of nodes and edges and movie set size: {self._graph.number_of_nodes()} and {self._graph.number_of_edges()} and {len(self._added_movies)}")

    # Takes in 2 lists of movie IDs to update the graph
    def _update_graph(self, id_set, actor1, actor2):
        movie_dict = dict()

        # Find the cast of every movie
        for movie in id_set:
            if movie in movie_dict or movie in self._added_movies:
                continue

            self._added_movies.add(movie)

            movie_item = tmdb.Movies(movie)
            movie_item.info()

            if {'id': 99, 'name': 'Documentary'} in movie_item.genres:
                continue
            
            movie_dict[movie] = set([actor['id'] for actor in movie_item.credits()['cast']])

        actor_set = set()

        # Add nodes and edges
        for movie, actors in movie_dict.items():
            actor_set.update(set(actors))
            for actor in actors:
                for co_actor in actors:
                    self._add_movie_connection(actor, co_actor, movie)

        pickle.dump(self._graph, open("tmdb_graph.pickle", "wb"))
        pickle.dump(self._added_movies, open("checked_movies.pickle", "wb"))
        if nx.has_path(self._graph, actor1, actor2):
            return []
        
        new_movie_set = set()

        # Compile every movie each actor has been in
        for actor in actor_set:
            actor_item = tmdb.People(actor)
            actor_item.info()

            new_movie_set.update(set([movie['id'] for movie in actor_item.movie_credits()['cast']]))

        return new_movie_set


    # Function to find the shortest path
    def find_connection(self, actor1, actor2):
        # Find ID for actors' names
        search1 = tmdb.Search()
        search2 = tmdb.Search()

        search1.person(query=actor1)
        search2.person(query=actor2)

        actor1_item = tmdb.People(search1.results[0]['id'])
        actor2_item = tmdb.People(search2.results[0]['id'])

        actor1_item.info()
        actor2_item.info()

        update_count = 0

        # Updates if either actor does not exist in graph (currently always updates)
        if True or not(self._graph.has_node(actor1_item.id) and self._graph.has_node(actor2_item.id)):
            movie_ids = set([movie['id'] for movie in actor1_item.movie_credits()['cast']])
            movie_ids.update(set([movie['id'] for movie in actor2_item.movie_credits()['cast']]))
            movie_ids = self._update_graph(movie_ids, actor1_item.id, actor2_item.id)
            update_count += 1
            # print(f"Updated number of nodes and edges: {self._graph.number_of_nodes()} and {self._graph.number_of_edges()}")

        # Initializes movie IDs if nodes exist but connection between does not
        elif not(nx.has_path(self._graph, actor1_item.id, actor2_item.id)):
            movie_ids = set([movie['id'] for movie in actor1_item.movie_credits()['cast']])
            movie_ids.update(set([movie['id'] for movie in actor2_item.movie_credits()['cast']]))
        
        # Updates if no connection exists
        while not(nx.has_path(self._graph, actor1_item.id, actor2_item.id)) and update_count < 6:
            print("Didn't connect, searching...")
            movie_ids = self._update_graph(movie_ids, actor1_item.id, actor2_item.id)
            update_count += 1
            print(f"Update count: {update_count}")
            print(f"Updated number of nodes and edges: {self._graph.number_of_nodes()} and {self._graph.number_of_edges()}")


        if nx.has_path(self._graph, actor1_item.id, actor2_item.id):
            id_path = nx.shortest_path(self._graph, source=actor1_item.id, target=actor2_item.id)

        else:
            print(f"No connection found after {update_count} updates")
            return
        
        name_path = []
        for actor_id in id_path:
            actor_item = tmdb.People(actor_id)
            actor_item.info()
            name_path.append(actor_item.name)

            if actor_id == id_path[-1]:
                continue

            connection_ids = self._graph[actor_id][id_path[id_path.index(actor_id) + 1]]
            connection_names = []

            # Gets all the movies that connect each actor
            for movie in connection_ids['movies']:
                movie_item = tmdb.Movies(movie)
                try:
                    movie_item.info()
                    connection_names.append(movie_item.title)
                except:
                    continue

            name_path.append(connection_names)

        for i in name_path:
            print(i)        
        

def main():
    actorgraph = ActorGraph()
    update = input("Would you like to update the graph? (y/n): ")
    if update.lower() == 'y':
        actorgraph.force_update()

    while True:
        actor1 = input("Enter the first actor: ")
        actor2 = input("Enter the second actor: ")
        actorgraph.find_connection(actor1, actor2)

        msg = input("Would you like to exit? (y/n): ")
        if msg.lower() == 'y':
            break

if __name__ == "__main__":
    main()
