def load_company_data(dir_path: str):
    documents = []
    
    df = pd.read_csv(f'{dir_path}/company_processed.csv')
    for idx, row in tqdm(df.iterrows(), desc="load company descriptions"):
        row = row.to_dict()
        if row["description"]:
            text = row.pop("description")
            documents.append(Document(
                text=text,
                #metadata=row,
                excluded_embed_metadata_keys=["Unnamed: 0", "legacyid", "industry", "country", "url"],
                excluded_llm_metadata_keys=["Unnamed: 0", "legacyid", "industry", "country", "url"],

            ))
    
    df = pd.read_csv(f'{dir_path}/company_qa_combined.csv')
    for idx, row in tqdm(df.iterrows(), desc="load company qna"):
        row = row.to_dict()
        if row["answer"] and row["question"]:
            text = f"Company: {row['companyName']} Question: {row['question']} Answer: {row['answer']}"
            row.pop('question')
            row.pop('answer')

            documents.append(Document(
                text=text,
                metadata=row,
                excluded_embed_metadata_keys=['question_id', 'fccid', 't1_x', 't2_x',
                                              'answer_id', 'date','ans_location','job_title'
                                              'fccompanyId', 'v1', 'v2'],
                excluded_llm_metadata_keys=['question_id', 'fccid', 't1_x', 't2_x',
                                              'answer_id', 'date','ans_location', 'job_title'
                                              'fccompanyId', 'v1', 'v2']
            ))

    return documents