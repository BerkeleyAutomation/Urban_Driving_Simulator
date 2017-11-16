import glob
import pickle
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn import tree

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
    if(len(states)<20): # bad demos that ended early
      continue
    for t in range(len(states)): # iterate through time
        if not actions[t][0] is None: # TODO: fix this, accel agents should't return None?
          X.append(np.array(states[t])) # TODO: fix this after state vectorization works
          y.append(actions[t][0])

  X = np.matrix(X)
  y = np.array(y)
  # TODO: add feature normalization
  print(X.shape)
  print(y.shape)

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
  validation_data = all_data[len(all_data)*8//10: len(all_data)]
  train_X, train_y = process_files(train_data)
  valid_X, valid_y = process_files(validation_data)

  model = RandomForestClassifier(n_estimators=10, criterion='gini', max_features=None, max_depth=15)

  model.fit(train_X, train_y)
  train_yp = model.predict(train_X)
  valid_yp = model.predict(valid_X)
  
  train_error = np.mean(train_y != train_yp)
  valid_error = np.mean(valid_y != valid_yp)


  # TODO: more informative printout
  print(len(train_data), len(validation_data))
  print(train_error, valid_error)

  pickle.dump(model, open("model.model", "wb"))

if __name__ == "__main__":
  learn()
