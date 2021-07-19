#suicide prediction program

'''
suicide prediction program is working 
            but 
will take time so dont quit in middle
'''

# import modules
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os
import json

# modules for encoding
from sklearn import preprocessing

#modules for data preparation
from sklearn.model_selection import train_test_split

#training models
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.metrics import accuracy_score, mean_squared_error, precision_recall_curve
from sklearn.linear_model import LogisticRegression

# sklearn modules for model creation
from sklearn.neighbors import KNeighborsClassifier

# sklearn module for tunning
from sklearn.model_selection import GridSearchCV


# data loading
#enter the location of your input file
input_location = input("Enter your input file location: ")
# check if the file exists
while not os.path.isfile(input_location):
    print("File does not exist")
    exit()
# Check input and read file
if(input_location.endswith(".csv")):
    data = pd.read_csv(input_location)
elif(input_location.endswith(".xlsx")):
    data = pd.read_excel(input_location)
else:
    print("ERROR: File format not supported!")
    exit()

# check data
variable = ['family_size', 'annual_income', 'eating_habits', 
            'addiction_friend', 'addiction', 'medical_history', 
            'depressed', 'anxiety', 'happy_currently', 'suicidal_thoughts']
if variable == list(data):
    print("Data is loaded")
else:
    print("Dataset doesnot contain: ", variable)
    exit()

# data preprocessing
# print(data.info())
# print("\n")
# print("Some of Data:\n")
# print(data.head())
# print("\n")


# data Cleaning
# total = data.isnull().sum()
# precentage = (total/len(data))*100
# missing_data = pd.concat([total, precentage], axis=1, keys=['Total', 'Precentage'])
# print("Missing Data:\n")
# print(missing_data)

# # fill missing data with mean value


# # drop unnecessary columns
if 'Timestamp' in data:
    data = data.drop(['Timestamp'], axis=1)
# print("\n")   
# print("Dataset afterdropping columns:\n")
# print(data.head())

# data encoding
labelDictionary = {}
for feature in data:
    le = preprocessing.LabelEncoder()
    le.fit(data[feature])
    le_name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    data[feature] = le.transform(data[feature])
    # Get labels
    labelKey = 'label_' + feature
    labelValue = [*le_name_mapping]
    labelDictionary[labelKey] =labelValue

# print(labelDictionary)
# for key, value in labelDictionary.items():     
#     print(key, value)

# print("\n")
# print("Dataset after encoding:\n")
# print(data.head())
# print("\n")

# output the encoded data
# data.to_csv(input_location + '_encoded.csv')
# print("\n")
# print("Encoded data saved as: " + input_location + '_encoded.csv')

# correlation matrix
corr = data.corr()
# print("\n")
# print("Correlation Matrix:\n")
# print(corr)
# print("\n")
f, ax = plt.subplots(figsize=(9, 9))
sns.heatmap(corr, vmax=.8, square=True, annot=True)
plt.show()
# plt.savefig('matrix.png')

#Splitting the data
independent_vars = ['family_size', 'annual_income', 'eating_habits', 
                    'addiction_friend', 'addiction', 'medical_history', 
                    'depressed', 'anxiety', 'happy_currently']
X = data[independent_vars] 
y = data['suicidal_thoughts']

#Splitting X and y into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)
#Dictionary to store accuracy results of different algorithms
accuracyDict = {}

#Acertaining the feature importance
frst = ExtraTreesClassifier(random_state = 0)
frst.fit(X,y)
imp = frst.feature_importances_
stan_dev = np.std([tree.feature_importances_ for tree in frst.estimators_], axis = 0)

indices = np.argsort(imp)[::-1]
labels = []
for f in range(X.shape[1]):
    labels.append(independent_vars[f])

plt.figure(figsize=(12,8))
plt.title("Feature importances")
plt.bar(range(X.shape[1]), imp[indices],
       color="g", yerr=stan_dev[indices], align="center")
plt.xticks(range(X.shape[1]), labels, rotation='vertical')
plt.xlim([-1, X.shape[1]])
plt.show()

#Tuning and evaluation of models
def evalModel(model, y_test, y_pred_class):
    acc_score = metrics.accuracy_score(y_test, y_pred_class)
    # print("Accuracy: ", acc_score)
    # print("NULL Accuracy: ", y_test.value_counts())
    # print("Percentage of ones: ", y_test.mean())
    # print("Percentage of zeros: ", 1 - y_test.mean())
    #creating a confunsion matrix
    conmat = metrics.confusion_matrix(y_test, y_pred_class)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    sns.heatmap(conmat, annot=True)
    plt.title("Confusion " + str(model))
    plt.xlabel("predicted")
    plt.ylabel("Actual")
    plt.show()
    return acc_score

# tuning the logistic regression model with Gridsearchcv
def log_reg_mod_tuning():
    print("\nTuning the Logistic Regression Model with GridSearchCV\n")
    param_grid = {'C':[0.1,1,10,100,1000],
                  'solver':['newton-cg','lbfgs','sag'],
                  'multi_class':['ovr','multinomial'],
                  'max_iter':[100,200,300,400,500]}
    log_reg = LogisticRegression()
    grid = GridSearchCV(log_reg, param_grid, cv=5, scoring='accuracy')
    grid.fit(X_train,y_train)
    print("Best parameters: ", grid.best_params_)
    print("Best cross-validation score: ", grid.best_score_*100, "%")
    print("Best estimator: ", grid.best_estimator_)
    lr = grid.best_estimator_
    y_pred_class = lr.predict(X_test)
    accuracy = evalModel(lr, y_test, y_pred_class)
    accuracyDict['Log_Reg_mod_tuning'] = accuracy * 100
log_reg_mod_tuning()

# tuning the KNN model with GridSearchCV
def tuneKNN():
    print("\nTuning KNN model with GridSearchCV\n")
    param_grid = {'n_neighbors':[3,5,7,9,11,13,15],
                  'weights':['uniform','distance'],
                  'algorithm':['auto','ball_tree','kd_tree','brute'],
                  'leaf_size':[10,20,30,40,50,60,70,80]}
    grid = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5)
    grid.fit(X_train,y_train)
    print("Best parameters: ", grid.best_params_)
    print("Best cross-validation score: ", grid.best_score_*100, "%")
    print("Best estimator: ", grid.best_estimator_)
    knn = grid.best_estimator_
    y_pred_class = knn.predict(X_test)
    accuracy = evalModel(knn, y_test, y_pred_class)
    accuracyDict['KNN'] = accuracy * 100
tuneKNN()

# tuning the Decision Tree model with GridSearchCV
def tuneDTree():
    print("\nTuning Decision Tree model with GridSearchCV\n")
    param_grid = {'criterion':['gini','entropy'],
                  'max_depth':[3,5,7,9,11,13,15],
                  'min_samples_split':[2,3,4,5,6,7,8],
                  'random_state':[0]}
    grid = GridSearchCV(DecisionTreeClassifier(), param_grid, cv=5)
    grid.fit(X_train,y_train)
    print("Best parameters: ", grid.best_params_)
    print("Best cross-validation score: ", grid.best_score_*100, "%")
    print("Best estimator: ", grid.best_estimator_)
    dt = grid.best_estimator_
    y_pred_class = dt.predict(X_test)
    accuracy = evalModel(dt, y_test, y_pred_class)
    accuracyDict['Decision_Tree'] = accuracy * 100
tuneDTree()

# tuning the Random Forest model with GridSearchCV
def tuneRF():
    print("\nTuning Random Forest model with GridSearchCV\n")
    param_grid = {'n_estimators':[10,20,30,40,50,60,70,80,90,100],
                  'max_depth':[3,5,7,9,11,13,15],
                  'min_samples_split':[2,3,4,5,6,7,8],
                  'criterion':['gini','entropy'],
                  'random_state':[0]}
    grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
    grid.fit(X_train,y_train)
    print("Best parameters: ", grid.best_params_)
    print("Best cross-validation score: ", grid.best_score_*100, "%")
    print("Best estimator: ", grid.best_estimator_)
    rf = grid.best_estimator_
    y_pred_class = rf.predict(X_test)
    accuracy = evalModel(rf, y_test, y_pred_class)
    accuracyDict['Random_Forest'] = accuracy * 100
tuneRF()

# #Logistic Regression Model
# def log_reg_mod():
#     #training the data in Log reg model
#     lr = LogisticRegression()
#     lr.fit(X_train,y_train)
#     #Predicting the data
#     y_pred_class = lr.predict(X_test)
#     accuracy = evalModel(lr, y_test, y_pred_class)
#     accuracyDict['Log_Reg'] = accuracy * 100
# log_reg_mod()

# #knn Model
# def knn():
#     knn = KNeighborsClassifier(n_neighbors=15)
#     knn.fit(X_train,y_train)
#     y_pred_class = knn.predict(X_test)
#     accuracy = evalModel(knn, y_test, y_pred_class)
#     accuracyDict['KNN'] = accuracy * 100
# knn()

# #Decision Tree Model
# def disTree():
#     dt = DecisionTreeClassifier(criterion='entropy')
#     dt.fit(X_train,y_train)
#     y_pred_class = dt.predict(X_test)
#     accuracy = evalModel(dt, y_test, y_pred_class)
#     accuracyDict['Decision Tree'] = accuracy * 100
# disTree()

# #Random Forest Model
# def randFor():
#     rf = RandomForestClassifier(n_estimators=20, random_state=1)
#     rf.fit(X_train,y_train)
#     y_pred_class = rf.predict(X_test)
#     accuracy = evalModel(rf, y_test, y_pred_class)
#     accuracyDict['Random Forest'] = accuracy * 100
# randFor()

print("accuracyDict:\n")
print(json.dumps(accuracyDict, indent=1))