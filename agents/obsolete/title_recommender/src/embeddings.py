import numpy as np 
import json 
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('sentence-transformers/msmarco-distilbert-dot-v5')

def load_jobs_data ():

    data = []
    with open('company_info_new.json') as f:
        for line in f:
            data.append(json.loads(line))

    all_jobs = set()	
    for i in range (len(data)): 
        for j in data[i]["popular_jobs"]: #["jobs_from_reviews"]: 
            #if "Industry" in data[i].keys():
            #    all_jobs.add(j + ", " + data[i]["Industry"])
            #else:
            all_jobs.add(j)
    return list (all_jobs)

def get_embeddings (job_title): 
    all_jobs_list = load_jobs_data()

    job_title_idx = all_jobs_list.index(job_title)

    embeddings = model.encode(all_jobs_list)
    sims = cosine_similarity ([embeddings[job_title_idx]], embeddings) #embeddings[1591]
    best = np.argsort(sims)

    top_10 = best[0,-10:][::-1]
    print ("Recommendations for job: ", job_title)

    top_10_names = []
    for i in top_10: 
        top_10_names.append(all_jobs_list [i])
    
    return top_10_names

#get_embeddings ("Tax Associate")