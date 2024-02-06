import pandas as pd
import pprint
from sklearn.feature_extraction.text import CountVectorizer , TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


df = pd.read_csv('datasets/tmdb.csv', encoding='utf-8')
# pprint.pprint(df['soup'])
# df = df.reset_index()
# print(df)
class RECOMMAND():
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer
        
    def get_recommandation(self , title):
        count  = self.vectorizer(stop_words="english")
        count_matrics = count.fit_transform(df['soup'])
        # pprint.pprint(count_matrics.index)

        cos_sim = cosine_similarity(count_matrics ,count_matrics)
        # print(cos_sim)
        indices = pd.Series(df.index, index=df['title'])
        # print(indices)
        idx = indices[title]
        sim_scores = list(enumerate(cos_sim[idx]))
        # print(sim_scores[0:10])
        data = sorted(sim_scores , key=lambda x:x[1] ,reverse=True)
        # print(data[0:10])
        sim_indices = data[1:11]
        sim_sorted = [x[0] for x in sim_indices]
        # print(sim_sorted)
        release_date = df['release_date'].iloc[sim_sorted]
        title = df['title'].iloc[sim_sorted]
        movie_df = pd.DataFrame(columns=['title', 'date'])
        movie_df['title'] = title
        movie_df['date'] = release_date
        # print(movie_df)
        return movie_df

# vectorizer = RECOMMAND(TfidfVectorizer)
# movie_df = vectorizer.get_recommandation('Avatar')
# print(movie_df)