
# coding: utf-8

# In[29]:


import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score


# In[30]:


data2 = pd.read_table("negative.csv", sep = ',', engine= 'python')


# In[31]:


print(data.columns.values)


# In[32]:


data=data2.dropna()


# In[33]:


data.tail()


# In[34]:


#le = preprocessing.LabelEncoder()
#data2['airline_sentiment'] = le.fit_transform(data2.airline_sentiment.values)


# In[35]:


#remove all '@' tags
new_text = []
import re
for tweet in data['tweets']:
   new_tweet = re.sub(r'@[A-Za-z0-9]+','',tweet).split()
   #stem_word=[ps.stem(word) for word in new_tweet if not word in set(stopwords.words('english'))]
   #stem_word = ' '.join(stem_word)
   new_text.append(new_tweet)
data['tweets'] = new_text
   
    


# In[36]:


data.head()


# In[37]:


import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


# In[38]:


#stemming
stem_tweet = []
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
ps = PorterStemmer()
for tweet in data["tweets"]:
        stem_word = [ps.stem(word) for word in tweet if not word in set(stopwords.words('english'))]
        stem_word = ' '.join(stem_word)
        stem_tweet.append(stem_word)
data['tweets'] = stem_tweet
        


# In[39]:


data.head()


# In[40]:


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score

for tweet in data["tweets"]:
    vectorizer = TfidfVectorizer(use_idf=True,lowercase=True,strip_accents='ascii')
    X = vectorizer.fit_transform(data["tweets"])


# In[41]:


y = data.sentiment
print(y.shape)
print(X.shape)


# In[42]:


x_train,x_test,y_train,y_test = train_test_split(X,y, random_state=42)


# In[43]:


clf = MultinomialNB()
clf.fit(x_train,y_train)


# In[47]:


predicted = clf.predict(x_test)


# In[48]:


print(accuracy_score(y_test, predicted))

