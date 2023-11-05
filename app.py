
from flask import Flask, request, render_template,jsonify
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
MAX_RETRIES = 5
def make_request(url):
    time.sleep(1)
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(20)  # Wait before retrying

    print(f"Failed to make request after {MAX_RETRIES} retries")
    return None
def get_all_particpate(contestname,contest_number,batchusers):
  p = 1
  users = []
  url =  "https://leetcode.com/contest/api/ranking/" + contestname + "-"+contest_number + "/?pagination=" + str(p) + "&region=india"
  response = make_request(url)
  if response.status_code == 200:
    total_no_of_pages = int(response.json()['user_num'])//25 + 1

    for p in range(1,total_no_of_pages+1):
      url =  "https://leetcode.com/contest/api/ranking/" + contestname + "-"+contest_number + "/?pagination=" + str(p) + "&region=india"
      response = make_request(url)
      if response.status_code == 200:
        user_pat = response.json()["total_rank"]
        
        for i in user_pat:
          print("scr",i['username'])
          users.append({'username' : i['username'],'rank' : i['rank'],'score':i['score']})
        
    dataframe = pd.DataFrame(users)
    all_handles = batchusers
    print(all_handles)
    all_handles.rename(columns = {'Roll No':'rollNum'}, inplace = True)
    all_handles.rename(columns = {'LEETCODE':'username'}, inplace = True)
    leetcode_handles = all_handles[['Name','rollNum',"username"]]
    m = pd.merge(leetcode_handles,dataframe,on = 'username', how = "left")
    m['rank'].fillna('-', inplace=True)
    m['score'].fillna('-', inplace=True)
    print(m)
    return m
app = Flask(__name__)
@app.route('/get_participate', methods=['POST'])
def get_participate():
    user = request.files['batchuser']
    if(user):
        batchusers = pd.read_csv(user)
        contestname = request.form['contestname']
        contest_number = request.form['contestnumber']
        print(contestname,contest_number)
        result = get_all_particpate(contestname,contest_number,batchusers)
        if not result.empty:
          result = result.to_dict(orient='records')
          print(result)
          return render_template('home.html', output= result)
        else:
          data = {
            'Name': [""],
            'rollNum': [""],
            'username': [""],
            'rank': [""],
            'score': [""]}
          df = pd.DataFrame(data)
          list_of_dicts = df.to_dict(orient='records')
          return render_template('home.html', output=list_of_dicts)
@app.route('/')
def hello_world():
  data = {
    'Name': [""],
    'rollNum': [""]
    ,'username': [""],
    'rank': [""],
    'score': [""]}
  df = pd.DataFrame(data)
  list_of_dicts = df.to_dict(orient='records')
  return render_template('home.html', output=list_of_dicts)
if __name__ == '__main__':
	app.run(host = '0.0.0.0')
