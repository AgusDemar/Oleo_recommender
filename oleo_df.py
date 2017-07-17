import pandas as pd
import numpy as np
#import sklearn.preprocessing 
#import surprise
#pd.set_option("display.max_columns",150)
#pd.set_option("display.height",1000)
#pd.set_option("display.max_rows",150)

## ENTRENAMIENTO 
# Abro el archivo -- cambiar la ruta 
train = pd.read_csv('./Dataset_Oleo/ratings_train.csv', encoding="ISO-8859-1")
test = pd.read_csv('./Dataset_Oleo/ratings_test.csv') 
ratings = pd.read_csv('./Dataset_Oleo/ratings.csv')
favoritos = pd.read_csv('./Dataset_Oleo/favoritos.csv')
restaurantes = pd.read_csv('./Dataset_Oleo/restaurantes.csv', encoding="ISO-8859-1")
siguiendo = pd.read_csv('./Dataset_Oleo/siguiendo.csv')
usuarios = pd.read_csv('./Dataset_Oleo/usuarios.csv', encoding="ISO-8859-1")

# Quitamos duplicados
#ratings = ratings.drop_duplicates(["id_usuario","id_restaurante","fecha"])
train = train.drop_duplicates(["id_usuario","id_restaurante","fecha"])
ids = train[["id_usuario","id_restaurante","fecha"]]
ids = test[["id_usuario","id_restaurante","fecha"]]
train[ids.duplicated(keep=False)]
test[ids.duplicated(keep=False)]
pd.value_counts(ids.duplicated())
# Obtenemos dummies
# Genre
#pd.value_counts(movie_genres["genre"].values, dropna = True)
movie_genres = pd.get_dummies(movie_genres, prefix= "gen", columns= ["genre"], dummy_na=True)
movie_genres = movie_genres.groupby("movieID", as_index=False).sum()

# Actors
#pd.value_counts(movie_actors["actorID"], ascending=False)
#movie_actors1 = movie_actors.loc[movie_actors["ranking"]<= 1]
#len(movie_actors1["actorName"].unique()) #7742
#movie_actors1 = pd.get_dummies(movie_actors1[["movieID","actorName"]], prefix= "act", columns=["actorName"])
actors_max = movie_actors.groupby("movieID")["ranking"].agg({"q_actors": np.max})
actors = movie_actors.groupby("actorID")["actorID"].agg({"actor_count": np.count_nonzero})

movie_actors1 = movie_actors[["movieID","actorID","ranking"]].merge(actors_max, how= "left", left_on= "movieID", right_index= True)
movie_actors1 = movie_actors1.merge(actors, how="left", left_on = "actorID", right_index = True)

best_3 = movie_actors1[movie_actors1["ranking"] <=3].groupby("movieID")["actor_count"].agg({"Best_3_count":np.sum})

movie_actors1 = movie_actors1.merge(best_3, how="left", left_on="movieID", right_index=True)
movie_actors1 = movie_actors1.groupby("movieID")["q_actors","actor_count","Best_3_count"].max()

# Directors
directors = movie_directors.groupby("directorID")["directorID"].agg({"director_count": np.count_nonzero})
movie_directors = movie_directors.merge(directors, how= "left", left_on= "directorID", right_index = True)

# Countries
#len(movie_locations["location1"].unique())
#len(movie_countries["country"].unique())
#pd.value_counts(movie_countries["country"].values)
movie_countries = pd.get_dummies(movie_countries, prefix="pais",dummy_na=True, columns=["country"])

# Imdb
movie_imdb1 = movie_imdb.loc[:,["imdbID","color","language", "content_rating"]]
movie_imdb1 = pd.get_dummies(movie_imdb1, prefix= ["col","lan","pub"], columns=["color","language", "content_rating"], dummy_na = True)
movie_imdb2= movie_imdb.drop(["color","director_name","actor_2_name","genres","actor_1_name","movie_title","actor_3_name","plot_keywords","movie_imdb_link","language","country","content_rating", "title_year"], 1)

# Juntamos train y test
train["Tipo"] = "Train"
test["Tipo"] = "Test"
all_data = pd.concat([train,test])

# Armamos all_data
all_data1 = pd.merge(all_data, movies[["id","imdbID","rtID"]], how="left", left_on ="movieID", right_on = "id")
all_data1.drop("id", axis = 1, inplace=True)
all_data2 = pd.merge(all_data1, movies_rt, how="left", on ="rtID")
all_data3 = pd.merge(all_data2, movie_imdb1, how = "left", on ="imdbID" )
all_data4 = pd.merge(all_data3, movie_imdb2, how="left", on="imdbID")
all_data5 = pd.merge(all_data4, movie_genres, how= "left", on= "movieID")
all_data6 = pd.merge(all_data5, movie_actors1, how="left", left_on= "movieID", right_index=True)
all_data7 = pd.merge(all_data6, movie_countries, how="left", on="movieID" )
all_data8 = pd.merge(all_data7, movie_directors.iloc[:,[0,3]], how="left", on= "movieID")

del all_data3

all_data8.drop(["imdbID","rtID"], axis=1, inplace=True)
all_data8.set_index(["userID","movieID"], inplace=True)
cols_to_drop = [col for col in list(all_data8) if col.startswith("date_")]
all_data8.drop(cols_to_drop, axis=1, inplace=True)

## Armamos train_def_user
train_def_user = all_data8[all_data8["Tipo"] == "Train"].drop("Tipo", axis = 1, inplace = False)

# Agregamos peso por rating
def mult_rating(df, column):
    df[column] = df[column] * df["rating"]
    return df[column]

cols_to_mult = [col for col in list(train_def_user) if col.startswith("col_") or col.startswith("pub_") or col.startswith("lan_") or col.startswith("gen_") or col.startswith("pais_")]
for col in cols_to_mult:
    mult_rating(train_def_user, col) 

# Imputamos na
pd.isnull(train_def_user).sum().sum()
train_def_user.fillna(0, inplace = True)

# MinMax Scale    
min_max_scaler = sklearn.preprocessing.MinMaxScaler()
train_minmax = pd.DataFrame(min_max_scaler.fit_transform(train_def_user), columns=train_def_user.columns, index=train_def_user.index)
train_minmax.head(10)

# Agrupamos por usuario
train_minmax.reset_index(inplace=True)
train_def_user = train_minmax.ix[:,train_minmax.columns != "movieID"].groupby("userID", as_index=True).mean()

## Armamos test_def_movie
test_def_movie = all_data8[all_data8["Tipo"] == "Test"].drop(["Tipo","rating"], axis=1, inplace=False)

# Imputamos na
pd.isnull(test_def_movie).sum().sum()
test_def_movie.fillna(0, inplace=True)

# MinMax Scale    
test_minmax = pd.DataFrame(min_max_scaler.fit_transform(test_def_movie), columns=test_def_movie.columns, index=test_def_movie.index)
test_minmax.head(10)

# Agrupamos por movie
test_minmax.reset_index(inplace=True)
test_def_movie = test_minmax.ix[:,test_minmax.columns != "userID"].groupby("movieID", as_index=True).mean()

# Nuevos Dataset_Oleo

train_def_user.to_csv("./Dataset/train_def_user.csv", index=False)
test_def_movie.to_csv("./Dataset/test_def_movie.csv", index=False)