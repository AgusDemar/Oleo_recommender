import pandas as pd
import os
import random
from surprise import Reader
from surprise import Dataset
from surprise import KNNWithMeans
from surprise import GridSearch
from surprise import dump
from surprise import evaluate
from surprise.accuracy import rmse
import collections
#import surprise

# Get top 10 function
def get_top_n(predictions, n=10):
    # First map the predictions to each user
    top_n = collections.defaultdict(list)
    for uid, iid, true_r, est, _ in predictions.items():
        top_n[uid].append((iid,est))
    
    # Then sort the predictions for each user and retrieve the k highest ones
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
        
    return top_n

# file paths
train_path = os.path.expanduser("./Dataset_Oleo/ratings_train.csv")
test_path = os.path.expanduser("./Dataset_Oleo/ratings_test.csv")
train = pd.read_csv("./Dataset_Oleo/ratings_train.csv", encoding="ISO-8859-1")
train = train.drop_duplicates(["id_usuario","id_restaurante","fecha"])
test = pd.read_csv("./Dataset_Oleo/ratings_test.csv", encoding="ISO-8859-1")
test[["rating_ambiente","rating_comida","rating_servicio"]] = 0

# Create different train
# Ambiente
train_ambiente = train.loc[:,["id_usuario","id_restaurante","rating_ambiente","fecha"]]
train_ambiente_path = "./Dataset_Oleo/train_ambiente.csv"
train_ambiente.to_csv("./Dataset_Oleo/train_ambiente.csv", index = False)

# Comida
train_comida = train.loc[:,["id_usuario","id_restaurante","rating_comida","fecha"]]
train_comida_path = "./Dataset_Oleo/train_comida.csv"
train_comida.to_csv("./Dataset_Oleo/train_comida.csv", index = False)

# Servicio
train_servicio = train.loc[:,["id_usuario","id_restaurante","rating_servicio","fecha"]]
train_servicio_path = "./Dataset_Oleo/train_servicio.csv"
train_servicio.to_csv("./Dataset_Oleo/train_servicio.csv", index = False)

# Create different tests
# Ambiente
test_ambiente = test.loc[:,["id_usuario","id_restaurante","rating_ambiente","fecha"]]
test_ambiente_path = "./Dataset_Oleo/test_ambiente.csv"
test_ambiente.to_csv("./Dataset_Oleo/test_ambiente.csv", index = False)

# Comida
test_comida = test.loc[:,["id_usuario","id_restaurante","rating_comida","fecha"]]
test_comida_path = "./Dataset_Oleo/test_comida.csv"
test_comida.to_csv("./Dataset_Oleo/test_comida.csv", index = False)

# Servicio
test_servicio = test.loc[:,["id_usuario","id_restaurante","rating_servicio","fecha"]]
test_servicio_path = "./Dataset_Oleo/test_servicio.csv"
test_servicio.to_csv("./Dataset_Oleo/test_servicio.csv", index = False)

# Reader: sólo especificar el rango de ratings
reader = Reader(line_format="user item rating timestamp", rating_scale=(1,4), sep=",", skip_lines=1 )
#reader = Reader(line_format="user item timestamp rating", rating_scale=(0,5) )

# Establishing columns (user_id,item_id,rating)
train_ambiente = Dataset.load_from_file(train_ambiente_path, reader)
train_comida = Dataset.load_from_file(train_comida_path, reader)
train_servicio = Dataset.load_from_file(train_servicio_path, reader)
test_ambiente = Dataset.load_from_file(test_ambiente_path, reader)
test_comida = Dataset.load_from_file(test_comida_path, reader)
test_servicio = Dataset.load_from_file(test_servicio_path, reader)

# Test with ambiente
# Shuffling ratings
raw_ratings = train_ambiente.raw_ratings  
random.shuffle(raw_ratings)

# A= 90%, B=10%
threshold = int(.9*len(raw_ratings))
A_raw_ratings = raw_ratings[:threshold]
B_raw_ratings = raw_ratings[threshold:]

train_ambiente.raw_ratings = A_raw_ratings

# Folds
train_ambiente.split(n_folds=3)

algo = KNNWithMeans()

evaluate(algo,train_ambiente)

## GridSearch with KNNWithMeans

param_grid = {"k": [60,80],
              "min_k": [4,6],      
              "sim_options": [{"name":"cosine",
                              "user_based":True},
                              {"name":"cosine",
                              "user_based":False},
                              {"name":"pearson",
                               "user_based":True},
                              {"name":"pearson",
                               "user_based":False},
                              {"name":"pearson_baseline",
                               "user_based":True,
                               "shrinkage":0},
                              {"name":"pearson_baseline",
                               "user_based":True,
                               "shrinkage":10},
                              {"name":"pearson_baseline",
                               "user_based":True,
                               "shrinkage":50},
                              {"name":"pearson_baseline",
                               "user_based":True,
                               "shrinkage":100},
                              {"name":"pearson_baseline",
                               "user_based":False,
                               "shrinkage":0},
                              {"name":"pearson_baseline",
                               "user_based":False,
                               "shrinkage":10},
                              {"name":"pearson_baseline",
                               "user_based":False,
                               "shrinkage":50},
                              {"name":"pearson_baseline",
                               "user_based":False,
                               "shrinkage":100}
                              ]
              }

grid_search = GridSearch(KNNWithMeans, param_grid, measures=["rmse"])

grid_search.evaluate(train_ambiente)

#Best RMSE score
grid_search.best_score["rmse"]

# Params with best RMSE score
grid_search.best_params["rmse"]

# Results
results_KNNWithMeans = pd.DataFrame.from_dict(dict([(k,pd.Series(v)) for k,v in grid_search.cv_results.items()]))
params = results_KNNWithMeans["params"].apply(pd.Series)
sim_options = params["sim_options"].apply(pd.Series)
results_KNNWithMeans = pd.concat([results_KNNWithMeans.loc[:,["RMSE","k"]],params["min_k"],sim_options], axis=1   )

results_KNNWithMeans.to_csv("./cv_results/KNNMeans.csv")

# Retrain best estimator on whole set A
trainset = train_ambiente.build_full_trainset()
algo = grid_search.best_estimator["RMSE"]
algo.train(trainset)

testset_1 = train_ambiente.construct_testset(B_raw_ratings)
predictions = algo.test(testset_1)

##########################################################################
# Build a pandas dataframe with predictions
def get_Iu(uid):
    try:
        return len(trainset.ur[trainset.to_inner_uid(uid)] )
    except ValueError: #user was not part of the trainset
        return 0

def get_Ui(iid):
    try:
        return len(trainset.ur[trainset.to_inner_uid(iid)])
    except ValueError:
        return 0

results_test = pd.DataFrame(predictions, columns=["uid", "iid", "rui", "est", "details"])
results_test["Iu"] = results_test.uid.apply(get_Iu)
results_test["Ui"] = results_test.iid.apply(get_Ui)
results_test["error"] = abs(results_test.est - results_test.rui)

best_predictions = results_test.sort_values(by="error")[:10]
worst_predictions = results_test.sort_values(by="error")[-10:]


# Print the recommended items for each user
top_n = get_top_n(predictions)

for uid, user_ratings in top_n.items():
    print(uid, [iid for (iid, _) in user_ratings])

# Print the k nearest neighbors of a user/item
get_neighbors = algo.get_neighbors(id, k=10)

# Convert inner ids into names
get_neighbors = (algo.testset.to_raw_iid(inner_id)
                for inner_id in get_neighbors)

##########################################################################

# Make predictions
data = Dataset.load_from_folds([(train_path, test_path)], reader)
#train = Dataset.load_from_file(train_path, reader)
#trainset = train.build_full_trainset()
#algo.train(trainset)
#predictions = evaluate(algo,testset)

# Dump algorithm and predictions
file_name = os.path.expanduser("./models/knn-mean")
dump.dump(file_name, predictions, algo)
loaded_predictions, loaded_algo = dump.load(file_name)

for trainset, testset in data.folds(): 
    loaded_algo.train(trainset)                             
    predictions = loaded_algo.test(testset)
    rmse(predictions)

#trainset = train.build_full_trainset()
#loaded_algo.train(trainset)
#print("Algo= {0}, k= {1}, min_k= {2}, sim={3}".format(loaded_algo.__class__.__name__, loaded_algo.k, loaded_algo.min_k, loaded_algo.sim_options))
#predictions = loaded_algo.test(testset)

# Save predictions
pred_def = pd.DataFrame(predictions, columns=["userID","movieID","rating"])
pred_def.to_csv("./output/demar_2.csv", index=False)