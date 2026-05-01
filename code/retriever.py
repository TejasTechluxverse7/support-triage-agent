import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

class DocumentRetriever:
    def __init__(self, corpus_dir="../corpus"):
        self.corpus_dir = corpus_dir
        self.documents = []
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.tfidf_matrix = None
        self.is_fitted = False
        self._load_corpus()
        
    def _load_corpus(self):
        if not os.path.exists(self.corpus_dir):
            return
            
        for filepath in glob.glob(os.path.join(self.corpus_dir, "**", "*.txt"), recursive=True):
            parts = filepath.split(os.sep)
            product_tag = parts[-2] if len(parts) >= 2 else "General"
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 30]
            if not chunks:
                chunks = [c.strip() for c in content.split('\n') if len(c.strip()) > 30]
                
            for chunk in chunks:
                self.documents.append({
                    "product": product_tag.lower(),
                    "text": chunk,
                    "source": os.path.basename(filepath),
                    # Pre-calculate normalized tokens for keyword overlap
                    "tokens": set(chunk.lower().translate(str.maketrans('', '', string.punctuation)).split())
                })
                
        if self.documents:
            texts = [doc["text"] for doc in self.documents]
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            self.is_fitted = True

    def _keyword_overlap_score(self, query_tokens, doc_tokens):
        if not query_tokens: return 0.0
        overlap = query_tokens.intersection(doc_tokens)
        return len(overlap) / len(query_tokens)

    def retrieve(self, query, company="None", top_k=1):
        if not self.is_fitted:
            return [], 0.0
            
        query_vec = self.vectorizer.transform([query])
        tfidf_similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        query_tokens = set(query.lower().translate(str.maketrans('', '', string.punctuation)).split())
        
        filtered_indices = []
        company_lower = str(company).lower()
        
        for i, doc in enumerate(self.documents):
            # Strictly filter by company (no cross-domain leakage)
            if company_lower in doc["product"] or doc["product"] in company_lower or company_lower == "none":
                filtered_indices.append(i)
                
        if not filtered_indices:
            return [], 0.0
            
        # Calculate combined score: 0.7 * tfidf + 0.3 * keyword_match
        scored_indices = []
        for i in filtered_indices:
            tfidf_score = tfidf_similarities[i]
            kw_score = self._keyword_overlap_score(query_tokens, self.documents[i]["tokens"])
            combined_score = (0.7 * tfidf_score) + (0.3 * kw_score)
            scored_indices.append((i, combined_score))
            
        # Sort by combined score
        scored_indices.sort(key=lambda x: x[1], reverse=True)
        best_indices = scored_indices[:top_k]
        
        results = []
        best_score = 0.0
        if best_indices:
            best_score = best_indices[0][1]
            for idx, score in best_indices:
                results.append({
                    "text": self.documents[idx]["text"],
                    "source": self.documents[idx]["source"],
                    "score": score
                })
                
        return results, best_score
