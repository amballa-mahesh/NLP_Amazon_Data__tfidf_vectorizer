# -*- coding: utf-8 -*-
"""NLP_Amazon_Data_ tfidf_vectorizer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GOkddFulV1Ao5fb0gMGDw7u2WNBTslfE
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np

df = pd.read_csv('/content/drive/MyDrive/35.1AmazonMobileDataUncleaned.csv')

df.head()

df.shape

"""# Conversion of Decision column to numeric values

"""

df['decision'].replace({'positive':1,'negative':0},inplace =True)

df.head(20)

df.isnull().sum()

df['decision'].value_counts()

"""# Treating Unbalanced Data - Upsampling Techinique

"""

from sklearn.utils import resample
postive_data,negative_data = df['decision'].value_counts()
print(postive_data)
print(negative_data,'\n')
df_postive_data  = df[df['decision']==1]
df_negative_data = df[df['decision']==0]

df_negative_upsampled = resample(df_negative_data,replace =True,n_samples = postive_data)
df_upsampled = pd.concat([df_postive_data,df_negative_upsampled])
postive_values,negative_values = df_upsampled['decision'].value_counts()
print(postive_values)
print(negative_values)

import string
from string import punctuation
punc = list(punctuation)
for i in range(0,10):
  punc.append(str(i))

import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
from nltk import word_tokenize,sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords
stops = stopwords.words('english')
import re

stops.remove('no')
stops.remove('not')
stops.remove('nor')

ps = PorterStemmer()
lm = WordNetLemmatizer()

"""# Cleaning the Text"""

def cleaned_text(sen):  
  sen = re.sub(r"didn't", "did not", sen)
  sen = re.sub(r"don't", "do not", sen)
  sen = re.sub(r"won't", "will not", sen)
  sen = re.sub(r"can't", "can not", sen)
  sen = re.sub(r"wasn't", "do not", sen)
  sen = re.sub(r"should't", "should not", sen)
  sen = re.sub(r"could't", "could not", sen)  
  sen = re.sub(r"\'ve", " have", sen)
  sen = re.sub(r"\'m", " am", sen)
  sen = re.sub(r"\'ll", " will", sen)
  sen = re.sub(r"\'re", " are", sen)
  sen = re.sub(r"\'s", " is", sen)
  sen = re.sub(r"\'d", " would", sen)
  sen = re.sub(r"\'t", " not", sen)
  sen = re.sub(r"\'m", " am", sen)
  sen = re.sub(r"n\'t", " not", sen) 
  sen = sent_tokenize(sen.lower().strip())
  word_token = []
  words =[]
  words_list =[]
  w= []
  k =[]
  for sent in sen:
      word_token.append(word_tokenize(sent))
  for word in word_token:
      words = ' '.join([i for i in word])
      words_list.append(words)
  for i in words_list:
    for j in i:
      if j in punc:
        j = ''
      else:
        j = j
      w.append(j) 
  k = ''.join([i for i in w])
  k_words= word_tokenize(k)
  final_words =[lm.lemmatize(i) for i in k_words if i not in stops and len(i)>2]
  final_words = ' '.join([i for i in final_words])
  return(final_words)

punc

df_upsampled['cleaned_text'] = df_upsampled['uncleanedreview'].apply(cleaned_text)

df_upsampled.head()

df_upsampled.drop(columns = ['uncleanedreview'],axis =1,inplace =True)

df_upsampled.head()

df_upsampled.shape

from sklearn.model_selection import train_test_split

x = df_upsampled.drop(['decision'],axis =1)
y = df_upsampled['decision']

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size =0.2,stratify=y,random_state =123)

x_train.shape,x_test.shape,y_train.shape,y_test.shape

from sklearn.feature_extraction.text import TfidfVectorizer

tf = TfidfVectorizer(min_df = 5,ngram_range= (1,5))

tf.fit(df_upsampled['cleaned_text'].values)

x_train.head()

"""# Changing the data to vectors using TFIDF vectorizer"""

train_cleaned = tf.transform(x_train['cleaned_text'].values)
test_cleaned  = tf.transform(x_test['cleaned_text'].values)

train_cleaned.shape,y_train.shape

"""# Model Creation using GridSearchCV and MultinomialNB"""

# Commented out IPython magic to ensure Python compatibility.
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
import math
from sklearn.metrics import roc_curve,auc, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

l =[0.5,0.5]
alphas = np.array([0.0001,0.001,0.01,0.1,1,10,100,1000,10000])
param_grid = {'alpha':alphas}
model = MultinomialNB(class_prior = l,fit_prior = False)
neigh = GridSearchCV(model,param_grid,scoring='roc_auc',cv = 5,return_train_score=True,verbose=4)
neigh.fit(train_cleaned,y_train)

results = pd.DataFrame.from_dict(neigh.cv_results_)

best_param = results['param_alpha']
train_auc  = results['mean_train_score']
test_auc   = results['mean_test_score']
log_alphas = []
for i in range(0,len(best_param)):
  value = math.log10(best_param[i])
  log_alphas.append(value)
log_alphas.sort()

neigh.best_params_['alpha']

"""Accuracy Graph by alphas values

"""

plt.figure(figsize=(5,3))
plt.plot(log_alphas,train_auc,label = 'train_auc')
plt.plot(log_alphas,test_auc, label = 'test_auc')
plt.scatter(log_alphas, train_auc, label='Train AUC points')
plt.scatter(log_alphas, test_auc, label='Test AUC points')
plt.legend()
plt.show()
print(neigh.best_params_)
print(neigh.best_score_)
print('best alpha log value-  ',math.log10(neigh.best_params_['alpha']))

"""# Finding the Thershold value using the ROC- AUC"""

l = [0.5,0.5]
model = MultinomialNB(alpha=0.001,class_prior = l,fit_prior = False)
model.fit(train_cleaned,y_train)

y_train_prob = model.predict_proba(train_cleaned)[:,1]
y_test_prob  = model.predict_proba(test_cleaned)[:,1]

train_fpr,train_tpr, train_thershold = roc_curve(y_train,y_train_prob)
test_fpr, test_tpr,  test_thershold  = roc_curve(y_test,y_test_prob)

plt.figure(figsize=(5,4))
plt.plot(train_fpr, train_tpr, label = "train_auc = "+str(auc(train_fpr,train_tpr)))
plt.plot(test_fpr,  test_tpr,  label = "test_auc = "+str(auc(test_fpr,  test_tpr)))
plt.legend()
plt.grid()
plt.show()

thershold = train_thershold[np.argmax(train_tpr*(1-train_fpr))]
print(" best Thershold is - ", round(thershold,2))
print('Maximum value of tpr*(1-fpr) is - ',round(max(train_tpr*(1-train_fpr)),2))

"""# Confusion Matrix evaluation - Without Thershold Value"""

y_train_pred = model.predict(train_cleaned)
y_test_pred  = model.predict(test_cleaned)
plt.figure(figsize= (3,2))
sns.heatmap(confusion_matrix(y_train, y_train_pred), annot=True,fmt='d')
plt.ylabel('actual values')
plt.xlabel('predicted values')
plt.show()
plt.figure(figsize= (3,2))
sns.heatmap(confusion_matrix(y_test, y_test_pred)  ,annot=True,fmt='d')
plt.ylabel('actual values')
plt.xlabel('predicted values')
plt.show()

"""# Confusion Matrix evaluation - Thershold Value"""

predictions_train = []
for i in y_train_prob:
  if i>= thershold:
    predictions_train.append(1)
  else:
    predictions_train.append(0)
    
predictions_test = []
for i in y_test_prob:
  if i>= thershold:
    predictions_test.append(1)
  else:
    predictions_test.append(0)

plt.figure(figsize= (3,2))
sns.heatmap(confusion_matrix(y_train, predictions_train), annot=True,fmt='d')
plt.ylabel('actual values')
plt.xlabel('predicted values')
plt.show()
plt.figure(figsize= (3,2))
sns.heatmap(confusion_matrix(y_test, predictions_test )  ,annot=True,fmt='d')
plt.ylabel('actual values')
plt.xlabel('predicted values')
plt.show()

"""When Compared to Count Vectorizer technique Tfidf Vectorizer is performing better and MultiNomialNB is specially designed for text classification

"""