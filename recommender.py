import pandas as pd
from cmath import inf
import signal, re


# Function that controls keyboard interrupt
def handler(signum, frame):
    exit(0)


# Function that extracts data from de csv file
def extract():
    df = pd.read_csv('imdb.csv' , sep=',', encoding='latin-1')
    return df


# Function that returns relevant data (data used for evaluation) from a film in a dictionary
def data_name(data, name):
    ind = data[data['Name'] == name].index[0]
    film = data.loc[ind]
    return {'Index': ind, 'Rate': film['Rate'], 'Genre': film['Genre'], 'Violence': film['Violence'], 'Type': film['Type']}


# Function that evaluates the similarity between two films
def transform(data, name):
    print('\nEvaluando: ', name)
    info = data_name(data, name)
    print(info)
    evaluation = {}
    for film in data['Name'].values:
        count = 0
        if film != name:
            data_film = data_name(data, film)
            # The most important factor is the similarity in the name. For example, 
            # if the film given is Harry Potter and the Chamber of Secrets, the film 
            # that we should return is another Harry Potter film.
            for word in name.split():
                if word in film:
                    count += 2
            # After this, we evaluate the similarity in the rate, genre, violence and type.
            # The rate is evaluated by the difference between the rates of the two films.
            # If there is no rate, we assume it is bad, so we substract 5 to the count.
            try:
                count += float(data_film['Rate']) - float(info['Rate'])
            except:
                count -= 5
            # The genre is evaluated by the number of genres that are in common between the two films.
            for genre in data_film['Genre'].split(','):
                if genre in info['Genre'].split(','):
                    count += 0.5
            # The violence is a very important factor that must be equal between the two films, 
            # as this represents the kind of film that the viewer is looking for.
            if info['Violence'] != 'No Rate':
                if data_film['Violence'] == info['Violence']:
                    count += 0.5
                else:
                    count -= 0.5
            # The same thing happens with the type of film. If the viewer is looking for a
            # documentary, we should return another documentary.
            if info['Type'] != 'No Rate':
                if data_film['Type'] == info['Type']:
                    count += 1
                else:
                    count -= 1
        evaluation[film] = count
    # Devolvemos la mejor opción
    choice = -inf
    for key, value in evaluation.items():
        if value > choice:
            choice, chosen_film = value, key
    return chosen_film


# Function that returns the name of the film that is most similar to the one given
def load(data, film):
    print('\nRecomendación: ', film)
    print(data_name(data, film))


# Main function
if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    end = False
    data = extract()
    # We ask the user for the name of the film
    name = input('Introduce el nombre de una película: ')
    # If the name is not explicitly in the database, we try to find it
    if name not in data['Name'].values:
        # For each film, we count the number of words that are in common with the name given
        films = {}
        for film in data['Name'].values:
            if film not in films:
                films[film] = 0
                film_list = film.split()
                for word in name.split():
                    if re.search(word, film, re.I):
                        films[film] += 1
        # We obtain the films that have the most words in common
        choice = -inf
        for value in films.values():
            if value > choice:
                choice = value
        possible_options = []
        for film, value in films.items():
            if value == choice:
                possible_options.append(film)
        # If there are too many possible films, we decide not to 
        # recommend any film, as the search was not specific enough.
        if len(possible_options) < 50:
            # If there is only one possible film, we ask for confirmation
            # If not, we ask the user to choose one of the possible films
            if len(possible_options) > 1:
                print('\nEstos son los resultados que hemos encontrado:\n')
                for ind, film in enumerate(possible_options):
                    print(f'\t{ind + 1}. {film}')
                print(f'\t{ind + 2}. Ninguno de los anteriores')
                option = input('\nElige una opción: ')
                while option not in [str(i) for i in range(1, len(possible_options) + 2)]:
                    print('Opción no válida')
                    option = input('\nElige una opción: ')
                if option == str(len(possible_options) + 1):
                    end = True
                else:
                    name = possible_options[int(option) - 1]
            else:
                found = input(f'\n¿Quieres decir {possible_options[0]}? (s/n): ')
                while not re.search(found, 'sn', re.I):
                    print('Opción no válida')
                    found = input(f'\n¿Quieres decir {possible_options[0]}? (s/n): ')
                if re.search(found, 's', re.I):
                    name = possible_options[0]
                else:
                    print('No hemos encontrado ninguna película con ese nombre.')
                    end = True
        else:
            print('\nNo hemos encontrado ninguna coincidencia exacta. Por favor sea más específico la próxima vez.')
            end = True
    if not end:
        film = transform(data, name)
        load(data, film)
    exit(0)

