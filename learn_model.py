import glob
import pickle
import numpy as np
from sklearn import svm

def process_files(list_of_paths):
  X = []
  y = []
  all_states = []
  for f in list_of_paths:
    data = pickle.load(open(f,"rb"))
    states = data[0]
    actions = data[1]
    assert(len(states) == len(actions))
    for t in range(len(states)): # iterate through time
      for i in range(len(actions[t])): # iterate through objects
        X.append([i]+states[t])
        if actions[t][i] == (0,-1):
          y.append(0)
        elif actions[t][i] == (0,0):
          y.append(1)
        elif actions[t][i] == (0,1):
          y.append(2)
        else:
          print("PANIC action not in action space")
  
  X = np.matrix(X)
  y = np.array(y)

  print(X.shape)
  print(y.shape)        

  return X,y       


if __name__ == "__main__":
  all_data = glob.glob("data/*dump.data")
  train_data = all_data[0:len(all_data)*8//10]
  validation_data = all_data[len(all_data)*8//10: len(all_data)]
  train_X, train_y = process_files(train_data)
  valid_X, valid_y = process_files(validation_data)
  model = svm.SVC()
  model.fit(train_X, train_y)
  train_yp = model.predict(train_X)
  valid_yp = model.predict(valid_X)
  train_error = np.mean( train_y != train_yp)
  valid_error = np.mean( valid_y != valid_yp)
  sanity_error = np.mean( train_yp != 2) 
  print(sanity_error, train_error, valid_error)
  pickle.dump(model, open("model.model", "wb"))

