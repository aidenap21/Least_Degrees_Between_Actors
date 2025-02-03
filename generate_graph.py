import tmdbsimple as tmdb
import networkx as nx
import pickle
import requests
from tmdb_api_key import api_key

class ActorGraph:
    def __init__(self):
        tmdb.API_KEY = api_key
        tmdb.REQUESTS_TIMEOUT = (2, 5)  # seconds, for connect and read specifically 
        tmdb.REQUESTS_SESSION = requests.Session()
        self.graph = pickle.load(open("tmdb_graph.pickle", "rb"))

    def add_movie_connection(self, actor1, actor2, movie):
        # Check if the edge already exists
        if self.graph.has_edge(actor1, actor2):
            # Append to the existing movie list
            self.graph[actor1][actor2]["movies"].add(movie)
        else:
            # Create a new edge with a list containing the movie
            self.graph.add_edge(actor1, actor2, movies=set([movie]))

    def regenerate(self):
        print("ARE YOU SURE YOU WANT TO REGENERATE?\nThis process will take an extended amount of time and will OVERWRITE the current graph.")
        confirm = input("Confirm (y/n): ")
        if confirm.lower() != 'y':
            print("Regeneration cancelled, exiting...")
            return
        
        # Create an empty graph
        self.graph = nx.Graph()

        movies_data = tmdb.Movies()
        movie_dict = dict()

        for movie in movies_data.popular()['results']:
            if movie['id'] in movie_dict:
                continue

            movie_item = tmdb.Movies(movie['id'])
            movie_item.info()

            movie_dict[movie['id']] = set([actor['id'] for actor in movie_item.credits()['cast']])

        # Add nodes and edges
        for movie, actors in movie_dict.items():
            for actor in actors:
                for co_actor in actors:
                    self.add_movie_connection(actor, co_actor, movie)
        
        pickle.dump(self.graph, open("tmdb_graph.pickle", "wb"))

    # Takes in 2 lists of movie IDs to update the graph
    def _update_graph(self, id_set, actor1, actor2):
        movie_dict = dict()

        # Find the cast of every movie
        for movie in id_set:
            if movie in movie_dict:
                continue

            movie_item = tmdb.Movies(movie)
            movie_item.info()

            movie_dict[movie] = set([actor['id'] for actor in movie_item.credits()['cast']])

        actor_set = set()

        # Add nodes and edges
        for movie, actors in movie_dict.items():
            actor_set.update(set(actors))
            for actor in actors:
                for co_actor in actors:
                    self.add_movie_connection(actor, co_actor, movie)

        pickle.dump(self.graph, open("tmdb_graph.pickle", "wb"))
        if nx.has_path(self.graph, actor1, actor2):
            return []
        
        new_movie_set = set()

        # Compile every movie each actor has been in
        for actor in actor_set():
            actor_item = tmdb.People(actor)
            actor_item.info()

            new_movie_set.update(set([movie['id'] for movie in actor_item.movie_credits()['cast']]))

        return new_movie_set


    # Function to find the shortest path
    def find_connection(self, actor1, actor2):
        print(f"Initial number of nodes and edges: {self.graph.number_of_nodes()} and {self.graph.number_of_edges()}")
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
        if True or not(self.graph.has_node(actor1_item.id) and self.graph.has_node(actor2_item.id)):
            movie_ids = set([movie['id'] for movie in actor1_item.movie_credits()['cast']])
            movie_ids.update(set([movie['id'] for movie in actor2_item.movie_credits()['cast']]))
            movie_ids = self._update_graph(movie_ids, actor1_item.id, actor2_item.id)
            update_count += 1
            print("Added both actors to the graph")
        
        # Updates if no connection exists
        while not(nx.has_path(self.graph, actor1_item.id, actor2_item.id)) and update_count < 6:
            movie_ids = self._update_graph(movie_ids, actor1_item.id, actor2_item.id)
            update_count += 1
            print(f"Update count: {update_count}")


        if nx.has_path(self.graph, actor1_item.id, actor2_item.id):
            id_path = nx.shortest_path(self.graph, source=actor1_item.id, target=actor2_item.id)
            # return path
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

            connection_ids = self.graph[actor_id][id_path[id_path.index(actor_id) + 1]]
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

        print(f"Final number of nodes and edges: {self.graph.number_of_nodes()} and {self.graph.number_of_edges()}")
        
        

def main():
    actorgraph = ActorGraph()
    #actorgraph.regenerate()
    actor1 = input("Enter the first actor: ")
    actor2 = input("Enter the second actor: ")
    actorgraph.find_connection(actor1, actor2)

if __name__ == "__main__":
    main()
