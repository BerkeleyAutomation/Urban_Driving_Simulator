import glob
import pickle
import numpy as np
from sklearn import svm
from sklearn.model_selection import GridSearchCV, cross_val_score 
from sklearn import linear_model
from sklearn.neural_network import MLPRegressor
from copy import deepcopy

# Parameter Grids for sci-kit learn
#param_grid = [{'C': [.01, 1, 100], 'gamma': [1, 10, 100], 'kernel': ['rbf', 'linear']}]
#param_grid = [{'C': [10], 'gamma': [1], 'kernel': ['rbf']}]
#param_grid = [{'alpha': [0, .01, .1, 1, 10, 100]}, {'learning_rate_init':[.01, .1, 1, 10, 100]}]
param_grid = [{'alpha': [0]}, {'learning_rate_init':[1]}]


def process_files(list_of_paths):
  """
  Main function to be run to collect driving data. Make sure that a data folder exists in the root directory of the project!

  Parameters
  ----------
  list_of_paths : list
    List of all files that contain trajectory data gathered from calling collect_data.py

  Returns
  -------
  X,y
    X contains the features (vectorized state) of the data in a nxd numpy matrix where n in the number of samples collected and d is the dimension of the state vector. 
    y contains the labels (output actions) of the data a numpy array.  
  
  """

  X = []
  y = []
  all_states = []
  for f in list_of_paths:
    data = pickle.load(open(f,"rb"))
    states = data[0]
    actions = data[1]
    assert(len(states) == len(actions))
    for t in range(len(states)): # iterate through time
      for o in range(len(actions[t])): # iterate through objects
        if not actions[t][o] is None: # TODO: fix this, accel agents should't return None?
          print(states[t])
          X.append(np.array(states[t])) # TODO: fix this after state vectorization works
          y.append(actions[t][o][1])

  X = np.matrix(X)
  y = np.array(y)
  # TODO: add feature normalization
  print(X.shape)
  print(y.shape)        
  print(X)
  print(y)
  return X,y       


def learn():
  """
  Main function to be run to learn a model for imitation learning agents.
  Make sure that a data folder with more than 5 data points exists in the root directory of the project. 

  Examples
  --------
  python3 examples/learn_model.py

  """

  all_data = glob.glob("data/*dump.data")
  train_data = all_data[0:len(all_data)*8//10]
  validation_data = all_data[len(all_data)*8//10: len(all_data)] # TODO: fix when there are <5 files
  train_X, train_y = process_files(train_data)
  valid_X, valid_y = process_files(validation_data)
  #all_X, all_y = process_files(all_data)
  svc = svm.SVC(kernel='rbf')
  lr = linear_model.Lasso()
  mlp = MLPRegressor(hidden_layer_sizes=(100, 100, 100), learning_rate='adaptive', max_iter = 10000, tol=1e-5)
  model = GridSearchCV(estimator=mlp, param_grid=param_grid)
  print(train_X.shape)
  model.fit(train_X, train_y)
  train_yp = model.predict(train_X)
  valid_yp = model.predict(valid_X)
  """
  train_error = np.mean( train_y != train_yp)
  valid_error = np.mean( valid_y != valid_yp)
  sanity_error = np.mean( train_yp != 1)
  sanity_error2 = np.mean( train_y != 1)
  """
  train_error = np.mean(np.square(train_y - train_yp))
  valid_error = np.mean(np.square(valid_y - valid_yp))
  sanity_error = np.mean(train_yp < .5)
  sanity_error2 =  np.mean(train_y < .5)

  # TODO: more informative printout
  print(len(train_data), len(validation_data))
  print(sanity_error, sanity_error2, train_error, valid_error)
  pickle.dump(model, open("model.model", "wb"))

if __name__ == "__main__":
  learn()
