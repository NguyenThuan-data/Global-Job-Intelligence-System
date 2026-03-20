import logging
from fuzzywuzzy import fuzz

class JobDeduplicator:
    def __init__(self, use_dedup=True):
        self.use_dedup = use_dedup

    def deduplicate(self, jobs):
        if not self.use_dedup:
            return jobs
            
        logging.info(f"Deduplicating {len(jobs)} total jobs...")
        deduped = []
        
        for job in jobs:
            is_duplicate = False
            for d in deduped:
                title_score = fuzz.token_sort_ratio(job["Position"].lower(), d["Position"].lower())
                comp_score = fuzz.token_sort_ratio(job["Company"].lower(), d["Company"].lower())
                
                if title_score > 85 and comp_score > 85:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduped.append(job)
                
        logging.info(f"After deduplication: {len(deduped)} unique jobs.")
        return deduped
