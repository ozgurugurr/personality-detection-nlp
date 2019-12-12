# -*- coding: utf-8 -*-
"""naive_bayes.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dhOMFPcJ3EVtSTt7B_w-uioxH8m0F1_R

Colab'a Google drive'ı entegre ediyoruz. Kullanılacak olan veriseti Google Drive'da bulunmaktadır
"""

from google.colab import drive
drive.mount('/content/gdrive')

import pandas as pd

"""
  Google Drive'ımızın root pathi gdrive/My Drive oluyor. 
  Proje için gerekli verisetini mbti adında bir klasör oluşturup içerisine yüklüyoruz. 
  İlgili verisetinin pathi gdrive/My Drive/mbti/all_users.csv oluyor.
"""

df = pd.read_csv("gdrive/My Drive/mbti/all_users.csv", sep = ';', header = 0)

df

import matplotlib.pyplot as plt

"""
  Verisetinin class tiplerine göre dağılım
"""

fig = plt.figure(figsize=(8,6))

df.groupby('type').type.count().plot.bar(ylim=0)
plt.show()

"""
  Verisetindeki I/E dağılımını göstermektedir. 
  I olanlar x ekseninde 0 olarak E olanlar ise 1 olarak gösterilmektedir
"""

fig = plt.figure(figsize=(8,6))

df.groupby('E').type.count().plot.bar(ylim=0)
plt.show()

"""
  Verisetindeki S/N dağılımını göstermektedir. 
  N olanlar x ekseninde 0 olarak S olanlar ise 1 olarak gösterilmektedir
"""

fig = plt.figure(figsize=(8,6))

df.groupby('S').type.count().plot.bar(ylim=0)
plt.show()

"""
  Verisetindeki T/F dağılımını göstermektedir.
  F olanlar x ekseninde 0 olarak T olanlar ise 1 olarak gösterilmektedir
"""

fig = plt.figure(figsize=(8,6))

df.groupby('T').type.count().plot.bar(ylim=0)
plt.show()

"""
  Verisetindeki J/P dağılımını göstermektedir. 
  P olanlar x ekseninde 0 olarak J olanlar ise 1 olarak gösterilmektedir
"""

fig = plt.figure(figsize=(8,6))

df.groupby('J').type.count().plot.bar(ylim=0)
plt.show()

"""
  Stop words, drive'da /mbti altındaki stop_words_tr.txt okunarak alınır
"""

from sklearn.feature_extraction.text import TfidfVectorizer

file = open("gdrive/My Drive/mbti/stop_words_tr.txt")
stop_word_list = file.read().split('\n')
file.close()

stop_word_list

"""
  Entrylere ön işleme adımları uygulanır. Bu adımlar:

  1.   Bütün harflerin küçük harf haline getirilmesi

  2.   'bkz', '--- spoiler ---', 'spoiler', '#12341324' (gibi böyle rakamların devam ettiği) entrylerin verisetinden çıkarılması gerekmektedir.

  3. Entrylerden stop words'ler silinmelidir.

  4. Web sitelerinin temizlenmesi

  5. Noktalama işaretlerinin temizlenmesi

  6. Rakamların temizlenmesi

  Temizlenme işlemlerinde empty string yerine space (' ') ile replace edilerek yapılmalıdır. Arından da fazla boşluklar vs trim edilmelidir.

  [+-]?([0-9]*)([.][0-9])? regex olarak kullanılacak hem rakamların silinmesinde hem de ondaklı sayıların silinmesinde

  Entrylerdeki harfler küçük harf haline getirilir
"""

df['entry'] = df['entry'].str.lower()

"""
  Dataframe içerisindeki bütün entrylere 'bkz', 'spoiler', '#' içerip içermediğine bakar 
  ve bunun sonucu index numarasıyla birlikte döner 15 True gibi.
  Bu demek oluyor ki 15 numaralı index bizim yazmış olduğumuz koşulu sağlamaktadır.
"""

indexes_contains_unwanted_words = df['entry'].str.contains('|'.join(['bkz', 'spoiler', r'#\d*']))

"""
  Dataframe'den ilgili entryler çıkartılır
"""

df = df[~indexes_contains_unwanted_words]
df.shape[0]

"""
  Entrylerden stop words silinir.
"""

df['entry'].str.replace('|'.join(stop_word_list), ' ')

"""Entrylerden web site linkleri silinir."""

df['entry'] = df['entry'].replace(r'http\S+', ' ', regex=True, inplace = True).replace(r'www\S+', '', regex=True, inplace = True)

"""
  Preprocessing işlemleri yapılır. 
  Burada bir tek Türkçe için stop words listesi kullanılarak girdilerden 
  gereksiz kelimeler atılır. TF-IDF özellik vektörü çıkarılır.
"""

tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words=stop_word_list, max_features=1000)

features = tfidf.fit_transform(df.entry).toarray()

labels = df.type

"""(x, y) -> x: döküman (entry) sayısı, y: kelime (vektör) sayısı
TF-IDF kullanarak çıkartılan özellik vektörü
"""

features.shape

"""
  Multinominal Naive Bayes modeli oluşturulur. 
  Oluşturulan bu model verisetinde "type" olarak belirtilen "analysts", "diplomats", "sentimenls", "explorers"
  sınıflarından hangilerine ait olduğunu tahmin etmek için kullanılır
"""

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

X_train, X_test, y_train, y_test = train_test_split(df['entry'], df['type'], random_state = 0)
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)

test_typeClass = y_test.values
   
predictions = clf.predict(count_vect.transform(X_test))

"""
Yapılacak tahminlerle ilgili istatistiksel verileri tutmak için predictions_result adında bir değişken oluşturulur.

Bu değişkenin yapısı aşağıdaki gibidir.

json
{
    "predicted": {
        "analysts":  { "actual": {"analysts": 0, "diplomats": 0, "explorers": 0, "sentinels": 0} }
        "diplomats": { "actual": {"analysts": 0, "diplomats": 0, "explorers": 0, "sentinels": 0} }
        "explorers": { "actual": {"analysts": 0, "diplomats": 0, "explorers": 0, "sentinels": 0} }
        "sentinels": { "actual": {"analysts": 0, "diplomats": 0, "explorers": 0, "sentinels": 0} }
    }
}


* Yapılan tahminlerle ilgili verilere ulaşabilmek için

    predictions_results['predicted']


* Yapılan tahminin analyst ise:

    predictions_results['predicted']['analysts'] 


* Yapılan analyst tahmininin gerçek değerlerine erişmek için:     

    predictions_results['predicted']['analysts']['actual']  


* Test verisi, model tarafından analysts olarak tahmin edilmiştir ve bu verinin gerçek değeri de analysts'tir.

    predictions_results['predicted']['analysts']['actual']['analysts']
"""

prediction_results = {'predicted': {}}  ## prediction_result['analysts'] means prediction is 'analysts'

prediction_results['predicted']['analysts']  = {'actual': {'analysts': 0, 'diplomats': 0, 'explorers': 0, 'sentinels': 0}}
prediction_results['predicted']['diplomats'] = {'actual': {'analysts': 0, 'diplomats': 0, 'explorers': 0, 'sentinels': 0}}
prediction_results['predicted']['explorers'] = {'actual': {'analysts': 0, 'diplomats': 0, 'explorers': 0, 'sentinels': 0}}
prediction_results['predicted']['sentinels'] = {'actual': {'analysts': 0, 'diplomats': 0, 'explorers': 0, 'sentinels': 0}}

## prediction_result['analysts']['diplomats'] means prediction is analysts but actual value is diplomats

"""
  prediction_results içerisinde tutulan sayaçların değerleri arttırılır.
"""

for i in range(len(predictions)):
  predicted_value = predictions[i]
  actual_value = test_typeClass[i]
  prediction_results['predicted'][predicted_value]['actual'][actual_value] += 1

"""
  JSON formatına çevrilir dict tipi. 
  Bu sayede daha okunaklı bir şekilde print edilmiş olur. 
"""

import json

print(json.dumps(prediction_results, indent = 2))

"""
  İlgili field extract edilir dict yapısından.
"""

results = prediction_results['predicted']

"""
  Başarı oranı hesaplanır
"""

accuracy = (results['analysts']['actual']['analysts'] + results['diplomats']['actual']['diplomats'] + results['explorers']['actual']['explorers'] + results['sentinels']['actual']['sentinels']) / len(predictions)
accuracy

"""
  E/I boyutu tahmin edilir
"""

X_train, X_test, y_train, y_test = train_test_split(df['entry'], df['E'], random_state = 0)  ## Geri kalanlar S, T, J
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)

test_typeClass = y_test.values
   
predictions = clf.predict(count_vect.transform(X_test))

predictions

predicted = {}
predicted['I'] = {'actual': {'I': 0, 'E': 0}}
predicted['E'] = {'actual': {'I': 0, 'E': 0}}
predicted

"""
  Modelin tahminleri 1-0 şeklindedir. 
  1: evet bu değer demektir. 
  0: hayır bu değer değil demektir. 
  Verisetinde sütunun ismi E'dir. 
  Eğer ki modelin tahmini E ise 1 değerini verir. 
  predicted'teki ilgili değere erişebilmek adına int_to_class array'i kullanılır
"""

int_to_class = ['I', 'E']

for i in range(len(predictions)):
  predicted_value = int_to_class[predictions[i]]
  actual_value = int_to_class[test_typeClass[i]]
  predicted[predicted_value]['actual'][actual_value] += 1

predicted

accuracy = (predicted['E']['actual']['E'] + predicted['I']['actual']['I']) / len(predictions)

accuracy

"""
  S/N boyutu tahmin edilir.
"""

X_train, X_test, y_train, y_test = train_test_split(df['entry'], df['S'], random_state = 0)  ## Geri kalan boyutlar: T, J
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)

test_typeClass = y_test.values
   
predictions = clf.predict(count_vect.transform(X_test))

predicted['N'] = {'actual': {'N': 0, 'S': 0}}
predicted['S'] = {'actual': {'N': 0, 'S': 0}}

predicted

int_to_class = ['N', 'S']

for i in range(len(predictions)):
  predicted_value = int_to_class[predictions[i]]
  actual_value = int_to_class[test_typeClass[i]]
  predicted[predicted_value]['actual'][actual_value] += 1

predicted

accuracy = (predicted['N']['actual']['N'] + predicted['S']['actual']['S']) / len(predictions)

accuracy

"""
  T/F boyutu tahmin edilir.
"""

X_train, X_test, y_train, y_test = train_test_split(df['entry'], df['T'], random_state = 0)  ##  J
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)

test_typeClass = y_test.values
   
predictions = clf.predict(count_vect.transform(X_test))

predicted['T'] = {'actual': {'T': 0, 'F': 0}}
predicted['F'] = {'actual': {'T': 0, 'F': 0}}

predicted

int_to_class = ['F', 'T']

for i in range(len(predictions)):
  predicted_value = int_to_class[predictions[i]]
  actual_value = int_to_class[test_typeClass[i]]
  predicted[predicted_value]['actual'][actual_value] += 1

predicted

accuracy = (predicted['F']['actual']['F'] + predicted['T']['actual']['T']) / len(predictions)

accuracy

"""
  J/P boyutu tahmin edilir.
"""

X_train, X_test, y_train, y_test = train_test_split(df['entry'], df['J'], random_state = 0) 
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)

test_typeClass = y_test.values
   
predictions = clf.predict(count_vect.transform(X_test))

predicted['J'] = {'actual': {'J': 0, 'P': 0}}
predicted['P'] = {'actual': {'J': 0, 'P': 0}}

predicted

int_to_class = ['P', 'J']

for i in range(len(predictions)):
  predicted_value = int_to_class[predictions[i]]
  actual_value = int_to_class[test_typeClass[i]]
  predicted[predicted_value]['actual'][actual_value] += 1

predicted

accuracy = (predicted['P']['actual']['P'] + predicted['J']['actual']['J']) / len(predictions)

accuracy

prediction_results['predicted'] = predicted

prediction_results