#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")
import matplotlib.pyplot as plt

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest , f_classif, chi2
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import matplotlib
from pandas.tools.plotting import scatter_matrix
from tester import test_classifier

def createDataFrame(data_dict):
	rows = []
	for k in data_dict.keys():
		rows.append(data_dict[k])
	df = pd.DataFrame(rows)
	return df

### Task 1: Select what features you'll use.
# You will need to use more features

features_list = ['poi', 'salary','bonus','exercised_stock_options','total_stock_value',
  'deferred_income','long_term_incentive','restricted_stock',
 'total_payments', 'shared_receipt_with_poi', 'loan_advances',
 'expenses', 'from_poi_to_this_person', 'other', 'from_this_person_to_poi',  
 'director_fees','to_messages','deferral_payments','from_messages', 
 'restricted_stock_deferred']


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


print "Genaral Statistics about the dataset : Data Exploration"

print "total records in dataset: ", len(data_dict)
poi_count = 0
for k in data_dict.keys():
	if data_dict[k]['poi'] == 1:
		poi_count += 1

print "poi count: " , poi_count
print "non-poi count ", len(data_dict) - poi_count

print "total features: ", len(features_list)


### Task 2: Remove outliers

##for each features number of NAN values
df = createDataFrame(data_dict)

col_list = list(df.columns.values)


nanCount = 0
nan_col_count_dict = {}
for col in col_list:
	count = 0
	for i in df[col]:
		if i == 'NaN':
			count += 1

	nan_col_count_dict[col] = count

print "Number of NaN values for each of the features"
print nan_col_count_dict

print "----------------------------------------------"



##for each row how features have NAN values
nan_row_count_dict = {}
for i, j in df.iterrows():
	count = 0
	for col in col_list:
		if j[col] == 'NaN':
			count += 1
	# if count >= 18:
	# 	print i, " : " ,j['email_address'], " : " , count	
	# else:
	# print j
	nan_row_count_dict[i] = {'nan_count' : count, 'email' : j['email_address']}

print "Number of NaN values in each row"
# print nan_row_count_dict
print "----------------------------------------------"


'''
We can see that there are several rows for which there are only few features 
for which there exists values but we are not removing any rows as we already 
have very less data
'''

##removal of outliers : there are several rows where out of all features, only 2-3 features are 
##having values, so I am removing those rows

# i = 0
# for kkey in data_dict.keys():
# 	if i in [31, 62, 90, 101, 141]:
		# print type(data_dict[kkey])
		# print data_dict[kkey]
		# del data_dict[kkey]
	# i += 1	

df = df.drop('email_address',1)

features_list = ['poi', 'salary','bonus','exercised_stock_options','total_stock_value',
  'deferred_income','long_term_incentive','restricted_stock',
 'total_payments', 'shared_receipt_with_poi', 'loan_advances',
 'expenses', 'from_poi_to_this_person', 'other', 'from_this_person_to_poi',  
 'director_fees','to_messages','deferral_payments','from_messages', 
 'restricted_stock_deferred']


print "New General Statistics of data:"
print "total records in dataset: ", len(data_dict)
poi_count = 0
for k in data_dict.keys():
	if data_dict[k]['poi'] == 1:
		poi_count += 1

print "poi count: " , poi_count
print "non-poi count ", len(data_dict) - poi_count

print "total features: ", len(features_list)
print "----------------------------------------------"


### Task 3: Create new feature(s)

## adding 1 new features
## total_income = salary + total_stock_value
##first need to make all the NaN 0, so that it doesnt throw and error

for i in range(0, len(df['salary'])):
	if df.iloc[i]['salary'] == 'NaN':
		df.loc[i, 'salary'] = 0


for i in range(0, len(df['total_stock_value'])):
	if (df.loc[i, 'total_stock_value']) == 'NaN':
		df.loc[i, 'total_stock_value'] = 0
		
df['total_income'] = df['salary'] + df['total_stock_value']

for i in range(0, len(df['from_poi_to_this_person'])):
	if df.iloc[i]['from_poi_to_this_person'] == 'Nan':
		df.loc[i, 'from_poi_to_this_person'] = 0
	if df.loc[i, 'from_this_person_to_poi'] == 'NaN':
		df.loc[i, 'from_this_person_to_poi'] = 0

	if df.loc[i, 'from_messages'] == 'NaN':
		df.loc[i, 'from_messages'] = 0
	if df.loc[i, 'to_messages'] == 'NaN':
		df.loc[i, 'to_messages'] = 0



for kkey in data_dict.keys():
	row_dict = data_dict[kkey]
	sal = 0
	total_stock = 0
	if row_dict['salary'] == 'NaN':
		sal = 0
	else:
		sal = row_dict['salary']
		
	if row_dict['total_stock_value'] == 'NaN':
		total_stock = 0
	else:
		total_stock = row_dict['total_stock_value']
	row_dict['total_income'] = sal + total_stock
	data_dict[kkey] = row_dict



##adding new feature into the feature list
# features_list = ['poi', 'salary','bonus','exercised_stock_options','total_stock_value',
#   'deferred_income','long_term_incentive',
#  'total_payments', 'shared_receipt_with_poi', 
#  'expenses', 'from_poi_to_this_person', 'other', 'from_this_person_to_poi',  
#  'to_messages','deferral_payments','from_messages', 
#  'restricted_stock_deferred', 'total_income']

features_list = ['poi', 'salary','bonus','exercised_stock_options','total_stock_value',
  'deferred_income','long_term_incentive','restricted_stock',
 'total_payments', 'shared_receipt_with_poi', 'loan_advances',
 'expenses', 'from_poi_to_this_person', 'other', 'from_this_person_to_poi',  
 'director_fees','to_messages','deferral_payments','from_messages', 
 'restricted_stock_deferred']



### Store to my_dataset for easy export below.
my_dataset = data_dict

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

features = MinMaxScaler().fit_transform(features)

from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.30, random_state=42)


print 'best features using kbestfeatures algorithm:'
kbest = SelectKBest(f_classif, k=len(features_list)-1)
selected_features = kbest.fit_transform(features,labels)
features_selected = [features_list[i+1] for i in kbest.get_support(indices=True)]
# print 'Features selected by SelectKBest:'
# print features_selected

selected_features = kbest.fit(features,labels)
transformed_ft = selected_features.transform(features)
feature_score = selected_features.scores_
for i in range(0, len(features_selected)):
	print features_selected[i], " ", feature_score[i]

print "--------------------------------------"





# print 'using PCA to find principal components'

# pca = PCA()


# # std_clf = Pipeline(steps=[('scaler', MinMaxScaler()),('pca', pca)])
# pca_clf = pca.fit(features)

# explained_ratio = pca_clf.explained_variance_ratio_

# arr = np.array(explained_ratio)
# # print arr
# # print np.cumsum(arr)

# new_df = df.drop('poi', 1)
# # print len(pca.components_)
# # print len(features_list)
# # print len(df.columns.values)
# # print len(new_df.columns.values)
# # print df.keys()
# # exit()

# dimensions = ['Dimension {}'.format(i) for i in range(1,len(pca.components_)+1)]
# components = pd.DataFrame(np.round(pca.components_, 4), columns = new_df.keys())
# components.index = dimensions


# ratios = pca.explained_variance_ratio_.reshape(len(pca.components_), 1)
# variance_ratios = pd.DataFrame(np.round(ratios, 4), columns = ['Explained Variance'])
# variance_ratios.index = dimensions


# fig, ax = plt.subplots(figsize = (14,8))
# components.plot(ax = ax, kind = 'bar');
# ax.set_ylabel("Feature Weights")
# ax.set_xticklabels(dimensions, rotation=0)


# for i, ev in enumerate(pca.explained_variance_ratio_):
# 	ax.text(i-0.40, ax.get_ylim()[1] + 0.05, "Explained Variance\n          %.4f"%(ev))

# # Return a concatenated DataFrame
# print pd.concat([variance_ratios, components], axis = 1)


###plotting PCA explained variance against number f principla components
# plt.figure(1, figsize=(4, 3))
# plt.clf()
# plt.axes([.2, .2, .7, .7])
# plt.plot(pca_clf.explained_variance_, linewidth=2)
# plt.axis('tight')
# plt.xlabel('n_components')
# plt.ylabel('explained_variance_')
# plt.show()

# exit()

print "--------------------------------------------"


# features_list = ['poi', 'exercised_stock_options',
# 'shared_receipt_with_poi',
#   'total_income', 'from_messages','total_stock_value',
# 'total_payments','deferral_payments','deferred_income',
# 'to_messages','from_poi_to_this_person', 'from_this_person_to_poi']


##trying to find results at different features count
# print "Printing score with different no of features"
# pca = PCA()
# clf_NB = GaussianNB()
# kbest = SelectKBest(f_classif)
# sk_fold = StratifiedShuffleSplit(n_splits=100, test_size=0.1, random_state=42)
# for i in range(1, len(features_list)):
# 	pipe = Pipeline(steps=[("selector", kbest),('pca', pca), ('NB', clf_NB)])
# 	parameters = {'selector__k': [i]}
# 	gs = GridSearchCV(pipe, param_grid = parameters, cv=sk_fold, scoring='f1')
	
# 	# gs.fit(features_train, labels_train)
# 	# print  i ," ", gs.score(features_test, labels_test)
# 	gs.fit(features, labels)
# 	clf = gs.best_estimator_
# 	print "For K = ", i
# 	test_classifier(clf, my_dataset, features_list)
print '----------------------------------------------'



####After finding that for k=15 we are getting max score we are adding 
#### newly created feature and now testing the score
print "Finding the Metric score after adding new feature into the features list"
features_list = ['poi', 'shared_receipt_with_poi','from_poi_to_this_person',
'loan_advances','from_this_person_to_poi','to_messages','director_fees',
'total_payments','deferral_payments','exercised_stock_options',
'deferred_income','total_stock_value','from_messages','bonus','other',
'restricted_stock', 'total_income']

my_dataset = data_dict

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

features = MinMaxScaler().fit_transform(features)
pca = PCA()
clf_NB = GaussianNB()
# sk_fold = StratifiedShuffleSplit(n_splits=100, test_size=0.1, 
	# random_state=42)
parameters = {}
pipe = Pipeline(steps=[('pca', pca), ('NB', clf_NB)])
gs = GridSearchCV(pipe, param_grid = parameters, cv=10, scoring='f1')
gs.fit(features, labels)
clf = gs.best_estimator_
test_classifier(clf, my_dataset, features_list)

print '----------------------------------------------'

'''
	
We are going to decide on the basis of accuracy of the Naive Baiyes how many features
we will be using.

'''


###finding correlation between all the features
# features_list.pop(0)

# # print np.cov(features)
# dff = pd.DataFrame(features, columns=features_list)
# corr_matrix = dff.corr()
# print corr_matrix
# print corr_matrix.columns.values


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html
my_dataset = data_dict
data = featureFormat(my_dataset, features_list, sort_keys = True)

labels, features = targetFeatureSplit(data)
from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.30, random_state=42)

sk_fold = StratifiedShuffleSplit(n_splits=100, test_size=0.1, random_state=42)
selector = SelectKBest(f_classif)

print "Trying various Algorithms : "

##GaussianNB
print 'GuassianNB'

# pca = PCA()
# clf_NB = GaussianNB()
# pipe = Pipeline(steps=[('pca', pca), ('NB', clf_NB)])

# parameters = {}
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_
# test_classifier(clf, my_dataset, features_list)
print "---------------------------------------------"

'''
Results : 
accuracy : 0.84107
Precision: 0.36992
Recall: 0.27300
F1: 0.31415
'''

#DecisionTree
print "DT"
# clf_DT = DecisionTreeClassifier()
# pipe = Pipeline(steps=[('DT', clf_DT)])

# parameters = {}
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_
# test_classifier(clf, my_dataset, features_list)
print "---------------------------------------------"
'''
Accuracy: 0.78600
Precision: 0.20020
Recall: 0.20200
F1: 0.201010

'''

##LogisticRegression
###Without scaler
print "LR"
# clf_REG = LogisticRegression()
# pipe = Pipeline(steps = [('REG', clf_REG)])
# parameters = {}
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_
# test_classifier(clf, my_dataset, features_list)
print "---------------------------------------------"

'''
Results
Accuracy: 0.76720
Precision: 0.20364	
Recall: 0.17900
F1: 0.19010
'''

##AdaBoost
print "ADA"
# clf_ADA = AdaBoostClassifier()
# pipe = Pipeline(steps = [('ADA', clf_ADA)])
# parameters = {}
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_
# test_classifier(clf, my_dataset, features_list)
print "---------------------------------------------"
'''
Results:
Accuracy : 0.79967
Recall : 0.18550
Precision : 0.21236
F1 : 0.19803
'''

##KNN
print "KNN"
# from sklearn.neighbors import KNeighborsClassifier
# clf_KNN = KNeighborsClassifier()
# pipe = Pipeline(steps = [('KNN', clf_KNN)])
# parameters = {}
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_
# test_classifier(clf, my_dataset, features_list)
print "---------------------------------------------"
'''
Accuracy: 0.87820
Precision: 0.61278
Recall: 0.23500
F1: 0.33972

'''


'''
We have used total 4 models to check our data and models accuracy, and we have 
found that Naive Bayes and DecisionTree are the 2 models that are giving max accuracy 
with best precision and recall and F1 score,
		Accuracy	recall 		Precision 		F1
NB 		0.84107		0.27300		0.36992			0.31415
DT 		0.78600		0.20020		0.20020			0.201010
LR 		0.76720		0.17900		0.20364			0.19010
ADA 	0.79967		0.18550		0.21236			0.19803
KNN 	0.87820		0.23500		0.61278			0.33972


'''

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!

features_list = ['poi', 'shared_receipt_with_poi','from_poi_to_this_person',
'loan_advances','from_this_person_to_poi','to_messages','director_fees',
'total_payments','deferral_payments','exercised_stock_options',
'deferred_income','total_stock_value','from_messages','bonus','other',
'restricted_stock']

my_dataset = data_dict
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)



###GuassianNB
print 'Guassian Naive Bayes'
# sk_fold = StratifiedShuffleSplit(n_splits=100, test_size=0.1, random_state=42)
# scaler = MinMaxScaler()
# selector = SelectKBest()
# pca = PCA()
# clf_NB = GaussianNB()
# parameters = {}
# pipe = Pipeline(steps=[('scaler', scaler), ('pca', pca), ('NB', clf_NB)])
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='precision')
# gs.fit(features, labels)
# clf = gs.best_estimator_
#print clf

# test_classifier(clf, my_dataset, features_list)
'''
Best NB algorithm after performance tuning
Pipeline(steps=[('scaler', MinMaxScaler(copy=True, feature_range=(0, 1))), 
	('pca', PCA(copy=True, iterated_power='auto', n_components=None, random_state=None,
  svd_solver='auto', tol=0.0, whiten=False)), ('NB', GaussianNB(priors=None))])

accuracy 	Precision 		Recall 		F1
0.81853		0.31237			0.30050		0.30632
'''

###KNN
print 'KNN'
# sk_fold = StratifiedShuffleSplit(n_splits=100, test_size=0.1, random_state=42)
# scaler = MinMaxScaler()

# clf_KNN = KNeighborsClassifier()
# parameters = {"KNN__n_neighbors": [2,3,4,5,10],
#     "KNN__algorithm" : ['auto', 'ball_tree', 'kd_tree', 'brute'],
#     "KNN__leaf_size": [20,30, 50,70,100]
# }
# pipe = Pipeline(steps=[('KNN', clf_KNN)])
# gs = GridSearchCV(pipe, param_grid=parameters, cv=sk_fold, scoring='f1')
# gs.fit(features, labels)
# clf = gs.best_estimator_

# test_classifier(clf, my_dataset, features_list)

'''
Best KNN algorithm after performance tuning
Pipeline(steps=[('KNN', KNeighborsClassifier(algorithm='auto', leaf_size=20, metric='minkowski',
           metric_params=None, n_jobs=1, n_neighbors=3, p=2,
           weights='uniform'))])
accuracy 	Precision 		Recall 		F1
0.87253		0.54247			0.28100		0.37022


'''


print 'Best algorithm that we have got is : KNN'

clf = Pipeline(steps=[('KNN', KNeighborsClassifier(algorithm='auto', leaf_size=20, metric='minkowski',
           metric_params=None, n_jobs=1, n_neighbors=3, p=2,
           weights='uniform'))])


test_classifier(clf, my_dataset, features_list)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.


dump_classifier_and_data(clf, my_dataset, features_list)

