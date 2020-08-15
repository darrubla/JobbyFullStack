from flask import Flask, request, make_response,redirect,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json
from flask import jsonify
import pandas as pd
import numpy as np
from pandasql import sqldf
from tabulate import tabulate

global df

df=[]
app = Flask(__name__, static_folder='../build', static_url_path='/')


#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:80085700@localhost:5432/jobby"
#db = SQLAlchemy(app)

def getArray(jobs):
    jobs = jobs.to_json()
    jobs = json.loads(jobs)
    jobsf = []
   
    
    for i in range(0,len(jobs['job_title'])):
        job=[]
        job.append(jobs['job_title'][str(i)])
        job.append(jobs['location'][str(i)])
        job.append(jobs['company_name'][str(i)])
        job.append(jobs['salary_estimate'][str(i)])
        job.append(jobs['rating'][str(i)])
        job.append(jobs['job_description'][str(i)])
        job.append(jobs['job_number'][str(i)])
        jobsf.append(job)
    return jobsf

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/data')
def data():
    
    df = pd.read_csv('static/DataAnalyst.csv')
    head  = df.head()

    for r in head.iterrows():
        print(r)
    return render_template('data.html',df = df)



@app.route('/hello')
def hello():
    return 'hola'

@app.route('/locations')
def locations():
    load()
    limpiar()
    locations=sqldf("select distinct(Location) from df ")
    locations = locations.to_json()
    print(locations)
    
    return render_template('datos.html',datos =locations)

@app.route('/salary/<keyword>')
def salary(keyword):
    load()
    limpiar()
    salary = keyword.split("-")
    l1 = str(int(salary[0])*1000)
    l2 = str(int(salary[1])*1000)
    print(l1)
    print(l2)
    jobs =sqldf("select * from df where  salary_estimate_l1 < "+l1+" and salary_estimate_l2 > "+l2)
    #jobs =sqldf("select * from df where (salary_estimate_l1 > "+l1+" and salary_estimate_l2 > "+l2+") or (salary_estimate_l1 < "+l1+" and salary_estimate_l2 > "+l2+") or (salary_estimate_l1 < "+l1+" and salary_estimate_l2 < "+l2)
    jobsf = getArray(jobs)
    print(jobsf)
    return jsonify(jobsf)

@app.route('/top/<keyword>')
def top(keyword):
    load()
    limpiar()
    jobs =sqldf("select * from df order by salary_estimate_l2 desc limit " + keyword)
    jobsf = getArray(jobs)
    print(jobsf)
    return jsonify(jobsf)

@app.route('/get/<keyword>')
def getId(keyword):
    load()
    limpiar()
    jobs =sqldf("select * from df where job_number = " + keyword )
    jobsf = getArray(jobs)
    return jsonify(jobsf)

@app.route('/search/<keyword>')
def searchKey(keyword):
    load()
    limpiar()
    jobs =sqldf("select * from df where job_title like '%" + keyword + "%' or Location like '%" + keyword + "%'")
    jobsf = getArray(jobs)
    
    return jsonify(jobsf)
   # return render_template('datos.html',datos =jobs)

def limpiar():
    global df
    df = df.dropna()
    df = df.replace(-1,np.nan)
    df = df.replace(-1.0,np.nan)
    df = df.replace('-1',np.nan)
    df.drop(['Unnamed: 0'], axis=1,inplace=True)
    df['Easy Apply'] = df['Easy Apply'].fillna(False).astype(bool)
    new=df["Salary Estimate"].str.split(" ", n = 1, expand = True)
    sal_range=new[0].str.split('-',n=1,expand=True)
    df['salary_estimate_l1'] = sal_range[0]
    df['salary_estimate_l2'] = sal_range[1]
    
    df['salary_estimate_l1']=df['salary_estimate_l1'].str.replace('K','000')
    df['salary_estimate_l1']=df['salary_estimate_l1'].str.replace('$','')
    df['salary_estimate_l1'] = df['salary_estimate_l1'].fillna(0)
    df['salary_estimate_l1']=df['salary_estimate_l1'].astype(str).astype(int)
    df['salary_estimate_l2']=df['salary_estimate_l2'].str.replace('K','000')
    df['salary_estimate_l2']=df['salary_estimate_l2'].str.replace('$','')
    df['salary_estimate_l2'] = df['salary_estimate_l2'].fillna(0)
    df['salary_estimate_l2']=df['salary_estimate_l2'].astype(str).astype(int)
    df['Founded']=df['Founded'].fillna(0).astype(int)
    df['job_number'] = df.index
    
    df_new = df.rename(columns={'Job Title': 'job_title',
                                'Salary Estimate':'salary_estimate',
                                'Job Description' : 'job_description',
                                'Rating' : 'rating',
                                'Company Name' : 'company_name',
                                'Company Name' : 'company_name',
                                'Location' : 'location',
                                'Company Name' : 'company_name',
                                'Headquarters' : 'headquarters',
                                'Size' : 'size',
                                'Founded' : 'founded',
                                'Type of ownership' : 'type_ownership',
                                'Industry' : 'industry',
                                'Sector' : 'sector',
                                'Revenue' : 'revenue',
                                'Competitors' : 'competitors',
                                'Easy Apply' : 'easy_apply',
                                } )
    
    #df_new.drop(['Salary Estimate'], axis = 1, inplace = True)
    
    cols =['job_number','job_title','salary_estimate','salary_estimate_l1','salary_estimate_l2',
          'job_description','rating','company_name','location',
          'headquarters','size','founded',
          'type_ownership','industry','sector','revenue','competitors','easy_apply']
    
    df_new=df_new[cols]

    df=df_new

    print("Datos limpios")

def load():
    global df
    df = pd.read_csv('static/DataAnalyst.csv')
    print("Datos cargados")

if __name__ == '__main__':
   
    app.run(port = 5000, debug = True)