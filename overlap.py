import tmdbsimple as tmdb
import requests
from tmdb_api_key import api_key

class HollywoodOverlap:
    def __init__(self):
        tmdb.API_KEY = api_key
        tmdb.REQUESTS_TIMEOUT = (2, 5)  # seconds, for connect and read specifically 
        tmdb.REQUESTS_SESSION = requests.Session()

    def between_movies(self):
        query1 = input("Enter movie 1: ")
        query2 = input("Enter movie 2: ")

        search1 = tmdb.Search()
        search2 = tmdb.Search()

        search1.movie(query=query1)
        search2.movie(query=query2)

        movie1 = tmdb.Movies(search1.results[0]['id'])
        movie2 = tmdb.Movies(search2.results[0]['id'])

        movie1.info()
        movie2.info()

        print(f"Comparing '{movie1.title}' and '{movie2.title}'")

        movie1_ids = set([actor['id'] for actor in movie1.credits()['cast']])
        movie2_ids = set([actor['id'] for actor in movie2.credits()['cast']])

        overlap = movie1_ids.intersection(movie2_ids)

        for id in overlap:
            person = tmdb.People(id)
            try:
                person.info()
                print(person.name)
            except:
                print(f"FAIL FOR {id}")

    def between_actors(self):
        query1 = input("Enter actor 1: ")
        query2 = input("Enter actor 2: ")

        search1 = tmdb.Search()
        search2 = tmdb.Search()

        search1.person(query=query1)
        search2.person(query=query2)

        actor1 = tmdb.People(search1.results[0]['id'])
        actor2 = tmdb.People(search2.results[0]['id'])

        actor1.info()
        actor2.info()

        print(f"Comparing '{actor1.name}' and '{actor2.name}'")

        actor1_ids = set([movie['id'] for movie in actor1.movie_credits()['cast']])
        actor2_ids = set([movie['id'] for movie in actor2.movie_credits()['cast']])

        overlap = actor1_ids.intersection(actor2_ids)

        for id in overlap:
            movie = tmdb.Movies(id)
            try:
                movie.info()
                print(movie.title)
            except:
                print(f"FAIL FOR {id}")


def main():
    overlap = HollywoodOverlap()
    choice = int(input("Overlap movies(1) or actors(2)?: "))
    if choice == 1:
        overlap.between_movies()
    else:
        overlap.between_actors()

if __name__ == "__main__":
    main()