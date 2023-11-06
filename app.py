
from flask import Flask, request, render_template,jsonify
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import concurrent.futures
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
def get_participants_page(url):
    pageusers = []
    response = make_request(url)
    if response and response.status_code == 200:
        user_pat = response.json()["total_rank"]
        for i in user_pat:
          pageusers.append({'username' : i['username'],'rank' : i['rank'],'score':i['score']})
          return pageusers
    return []
def get_all_participants(contestname, contest_number, batchusers):
  p = 1
  users = []
  url =  "https://leetcode.com/contest/api/ranking/" + contestname + "-"+contest_number + "/?pagination=" + str(p) + "&region=india"
  response = make_request(url)
  if response != None and response.status_code == 200:
    total_no_of_pages = int(response.json()['user_num'])//25 + 1

    url_template = "https://leetcode.com/contest/api/ranking/{}-{}/?pagination={}&region=india"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for page_num in range(1, total_no_of_pages + 1):
            url = url_template.format(contestname, contest_number, page_num)
            futures.append(executor.submit(get_participants_page, url))

        for future in concurrent.futures.as_completed(futures):
            users.extend(future.result())

    return users

app = Flask(__name__)

@app.route('/get_participate', methods=['POST'])
def get_participate():
    user = request.files['batchuser']
    if user:
        batchusers = pd.read_csv(user)
        contestname = request.form['contestname']
        contest_number = request.form['contestnumber']
        

        users = get_all_participants(contestname, contest_number, batchusers)

        if users:
            dataframe = pd.DataFrame(users)
            all_handles = batchusers
            all_handles.rename(columns={'Roll No': 'rollNum'}, inplace=True)
            all_handles.rename(columns={'LEETCODE': 'username'}, inplace=True)
            leetcode_handles = all_handles[['Name', 'rollNum', "username"]]
            merged_df = pd.merge(leetcode_handles, dataframe, on='username', how="left")
            merged_df['rank'].fillna('-', inplace=True)
            merged_df['score'].fillna('-', inplace=True)
            return render_template('home.html', output=merged_df.to_dict(orient='records'))
    
    data = {
        'Name': [""],
        'rollNum': [""],
        'username': [""],
        'rank': [""],
        'score': [""]
    }
    df = pd.DataFrame(data)
    return render_template('home.html', output=df.to_dict(orient='records'))

@app.route('/')
def hello_world():
    data = {
        'Name': [""],
        'rollNum': [""],
        'username': [""],
        'rank': [""],
        'score': [""]
    }
    df = pd.DataFrame(data)
    return render_template('home.html', output=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run()
