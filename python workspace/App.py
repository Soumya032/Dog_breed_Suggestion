from flask import Flask,render_template,request
import plotly.express as px
import pandas as pd
import numpy as np
app=Flask(__name__)

df = pd.read_csv('C:\\Users\\soumy\\Downloads\\akc-data-latest.csv')
df['group'].unique().tolist() # here two groups are wrong
df=df.rename(columns={'Unnamed: 0' : 'breed'})#renaming unnamed:0 to column breed
df=df.dropna() # removing rows with empty values as they will affect the model
df['group'].unique().tolist() #we can see that now we have all the valid groups
h='shedding_value'
h=('high_'+h).replace('_value','') # add high to column name and replace _value with empty i.e remove empty
for col in [col for col in df.columns if 'value' in col]: #creating new columns with high low and medium
    df[('high_'+col).replace('_value','')] = df[col].apply(lambda x: x >= .8) 
    df[('medium_'+col).replace('_value','')] = df[col].apply(lambda x: .4 <= x <= .8)
    df[('low_'+col).replace('_value','')] = df[col].apply(lambda x: x <= .4)
    
    df[col] = df[col].apply(lambda x: [x,0])
df[['grooming_frequency_value','grooming_frequency_category','high_grooming_frequency','medium_grooming_frequency','low_grooming_frequency']]
for col in ['height']:
    df[col] = (df['max_'+col]+df['min_'+col])/2
df[['max_height','min_height','height']]
for col in ['weight','expectancy']:
    df[col] = (df['max_'+col]+df['min_'+col])/2
df[['weight','expectancy']]
for col in ['height','weight','expectancy']:
    temp = df[col].describe(percentiles=[.2,.33,.4,.6,.67,.8]) #making new columns with the help of percentiles
    df['high_'+col] = df[col].apply(lambda x: x > temp['67%'])
    df['medium_'+col] = df[col].apply(lambda x: temp['33%'] < x < temp['67%'])
    df['low_'+col] = df[col].apply(lambda x: x < temp['33%'])
    #making value column for height,weight,expectancy
    df[col+'_value'] = df[col].apply(lambda x: '1' if x >= temp['80%'] else x)
    df[col+'_value'] = df[col+'_value'].apply(lambda x: '.8' if ((type(x)!=str) and (x >= temp['60%']) and (x < temp['80%'])) else x)
    df[col+'_value'] = df[col+'_value'].apply(lambda x: '.6' if ((type(x)!=str) and (x >= temp['40%']) and (x < temp['60%'])) else x)
    df[col+'_value'] = df[col+'_value'].apply(lambda x: '.4' if ((type(x)!=str) and (x >= temp['20%']) and (x < temp['40%'])) else x)
    df[col+'_value'] = df[col+'_value'].apply(lambda x: '.2' if ((type(x)!=str) and (x < temp['20%'])) else x) 
    df[col+'_value'] = df[col+'_value'].apply(lambda x: [float(x),0])
df[['min_weight','max_weight','weight','high_weight','medium_weight','low_weight','weight_value']]
df[['min_height','max_height','height','high_height','medium_height','low_height','height_value']]
rec_columns = ['group','temperament'] +[col for col in df.columns if any(substr in col for substr in['min_','max_','category'])] 
df['group'] = df['group'].apply(lambda x: x.replace(' ',''))
df['group'] = df['group'].apply(lambda x: x.replace('Group',''))



@app.route('/')
def index():
    return render_template('index.html',)

@app.route('/store')
def store():
        return render_template('store.html')
@app.route('/home')
def home():
 return render_template('home.html')

@app.route('/recommend', methods=['POST'])
def recommend():

   ## popularity = request.form.get('popularity')
   ## weight = request.form.get('weight')
   ## life_expectancy = request.form.get('life_expectancy')
   ## grooming_frequency = request.form.get('grooming_frequency')
   ## shedding = request.form.get('shedding')
   ## energy_level = request.form.get('energy_level')
   ## trainability = request.form.get('trainability')
   ## demeanor = request.form.get('demeanor')
   ## size = request.form.get('size')
   ## temperament = request.form.get('temperament')
   ##form_array=np.array([[popularity,weight, life_expectancy, grooming_frequency, shedding,energy_level, trainability, demeanor, size, temperament]])
   ##model=pickle.load(open("data_dog.pkl","rb"))
   ##recommendation = model.predict([form_array])[0]
 def recommend_popular_dogs(group=[],low=[],medium=[],high=[],breed=None):
    if type(group) == str:# incase there is only a single input the string will be converted to a string list
        group = [group]
    if type(low) == str:
        low = [low]
    if type(medium) == str:
        medium = [medium]
    if type(high) == str:
        high = [high]
    
    if breed is not None:
        breed_group = df[df['breed']==breed]['group'].iloc[0]
        group=[breed_group]
      
        
    temp = df.sort_values('popularity') #sorting the values based on the input and popularity
    if len(group) > 0:
        temp = temp[temp['group'].isin(group)]
    if len(low) > 0:
        for col in low:
            temp = temp[temp['low_'+col]]
    if len(medium) > 0:
        for col in medium:
            temp = temp[temp['medium_'+col]]
    if len(high) > 0:
        for col in high:
            temp = temp[temp['high_'+col]] 
            
    num_dogs = min(10,len(temp)) #takes whichever value is less
    
    for i in range(num_dogs):
        print('{}.'.format(i+1),temp['breed'].iloc[i])
    
    for i in range(num_dogs):
        print()
        print('{}.'.format(i+1),temp['breed'].iloc[i])
        print(temp['description'].iloc[i])
        print(temp[rec_columns].iloc[i])
    breed_list = temp['breed'].iloc[:10].tolist()
    temprament = temp['temperament'].iloc[:10].tolist()
    max_height = temp['max_height'].iloc[:10].tolist()
    shed = temp['shedding_category'].iloc[:10].tolist()
    train = temp['trainability_category'].iloc[:10].tolist()
    return breed_list,temprament,max_height,shed,train
 
 user_breed=request.form['breed_name']
 breed_list,temprament,max_height,shed,train=recommend_popular_dogs(breed=user_breed)
 return render_template('result.html',breedName=breed_list,breedTemp=temprament,breedHeight=max_height,breedShed=shed,breedTrain=train)


@app.route('/compare')
def compare():
    return render_template('comparision.html')

    
