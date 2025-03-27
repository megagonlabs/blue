import json
from pathlib import Path

import faiss
import fire
from llama_index.core import Document, StorageContext, ServiceContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from tqdm import tqdm


def load_data(dir_path: str):
    documents = []
    with tqdm(desc="load wikipedia", dynamic_ncols=True) as prog:
        for fp in Path(dir_path).rglob("kilt_*"):
            for line in open(fp):
                data = json.loads(line)
                if data["text"]:
                    text = ' '.join(data.pop("text"))
                    documents.append(Document(
                        text=text,
                        metadata=data,
                        excluded_embed_metadata_keys=["id", "revid", "url"],
                        excluded_llm_metadata_keys=["id", "revid", "url"]
                    ))
                prog.update()
    return documents


def run(raw_dir: str,
        persist_dir: str,
        embed_model: str = "facebook/contriever-msmarco",
        pooling: str = "mean",
        chunk_size: int = 256,
        chunk_overlap: int = 0,
        batch_size: int = 32):
    documents = load_data(raw_dir)
    embed_model = HuggingFaceEmbedding(model_name=embed_model, pooling=pooling, embed_batch_size=batch_size)

    d = embed_model._model.config.hidden_size
    faiss_index = faiss.IndexFlatL2(d)

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        llm=None
    )
    index = VectorStoreIndex.from_documents(documents,
                                            storage_context=storage_context,
                                            service_context=service_context,
                                            show_progress=True)
    index.storage_context.persist(persist_dir=persist_dir)


if __name__ == '__main__':
    fire.Fire(run)