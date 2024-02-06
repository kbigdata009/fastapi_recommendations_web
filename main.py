from fastapi import FastAPI ,Request ,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import status
import pandas as pd
import numpy as np
from datetime import date
from ml import RECOMMAND
import json
from fetch import movie , movie_collection
import requests
from sklearn.feature_extraction.text import CountVectorizer , TfidfVectorizer

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

df = pd.read_csv('datasets/tmdb.csv', encoding='utf-8')
all_titles = [df['title'][i] for i in range(len(df['title']))]

@app.get('/', response_class=HTMLResponse)
async def main(request: Request):
    year = date.today().year
    year_url = f'http://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&primary_release_year={year}&sort_by=popularity.desc'
    result = json.loads(requests.get('https://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&primary_release_year=2022&sort_by=popularity.desc').text)
    # print(result['results'][1])
    top_year = movie_collection()
    top_year.results=[]
    top_year.fetch(year_url)
    genre_url =f'https://api.themoviedb.org/3/genre/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&language=en-US'
    genres = json.loads(requests.get(genre_url).text)
    # print(genres)
    top_genre_collection = []
    for data in genres['genres']:
        # print(data['id'])
        genre_id = f'https://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genres={data["id"]}&sort_by=popularity.desc'
        # print(genre_id)
        top_genre = movie_collection()
        top_genre.fetch(genre_id)
        # for result in top_genre.results:
        #     print(result.title)
        top_genre_id = [top_genre.results , data['name']]
        top_genre_collection.append(top_genre_id)
    # for i in top_genre_collection:
    #     print(i[1])
        # for j in i[0]:
        #     print(j.title)
    # print(top_genre_collection[0][0])
    return templates.TemplateResponse(request=request,name="index.html" , context={"top_year":top_year.results, "year": year, "top_genre": top_genre_collection})

@app.post('/', response_class=HTMLResponse)
async def index_post(request: Request, search:str=Form(...)):
    # print(search)
    movie_dic = movie_collection()
    movie_dic.results=[]
    id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={search}"
    movie_dic.fetch(id_url)
    return templates.TemplateResponse(request=request, name='landing.html', context={"movie": movie_dic.results, "key_word": search})

@app.get('/details/{id}', response_class=HTMLResponse )
def details(request: Request , id ):
    url = f"http://api.themoviedb.org/3/movie/{id}?api_key=da396cb4a1c47c5b912fda20fd3a3336"
    data = json.loads(requests.get(url).text)
    data_json = movie(data["id"],data["title"],data["poster_path"],data["vote_average"],data["release_date"],data["overview"],data["backdrop_path"])
    return templates.TemplateResponse(request=request, name= 'details.html', context={"movie": data_json})

@app.get('/recommand', response_class=HTMLResponse)
def recommand(request: Request):
    return templates.TemplateResponse(request=request, name='recommand.html')

@app.post('/recommand', response_class=HTMLResponse)
def recommand_post(request: Request, movie_name:str=Form(...)):
    m_name = movie_name.title()
    if m_name not in all_titles:
        id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={m_name}"
        data = json.loads(requests.get(id_url).text)['results']
        name_list=[i['original_title'] for i in data]
            
        return templates.TemplateResponse(request=request, name='negative.html' , context={"name_list":name_list , "name":m_name} )
    else:
        vectorizer = RECOMMAND(TfidfVectorizer)
        result_df = vectorizer.get_recommandation(m_name)
        data=[]
        # print(list(result_df['title']))
        for i in range(len(result_df)):
            data.append((list(result_df["title"])[i] , list(result_df["date"])[i]))
        print(data)
        return templates.TemplateResponse(request=request, name='positive.html',context={"movie_data":data , "search_name":m_name})
        # print(name_list)    
        # return name_list
