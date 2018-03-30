#coding:utf-8
# 词干提取算法

from nltk import stem

input_words = ['movies','dogs','planes','flowers','flies','fries','fry \
','weeks', 'planted','running','throttle']


porter = stem.porter.PorterStemmer()
p_words = [porter.stem(w) for w in input_words]
print p_words

lancaster = stem.lancaster.LancasterStemmer()
l_words = [lancaster.stem(w) for w in input_words]
print l_words

snowball = stem.snowball.EnglishStemmer()
s_words = [snowball.stem(w) for w in input_words]
print s_words
