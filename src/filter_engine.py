class FilterEngine:
    def __init__(self, filters):
        self.filters = filters

    def classify_and_filter(self, jobs):
        classified = [self._classify_job(j) for j in jobs]
        return self._apply_filters(classified)

    def _classify_job(self, job):
        level = "Unknown"
        title_lower = job["Position"].lower()
        for l in self.filters.get("level", []):
            if l.lower() in title_lower:
                level = l
                break
                
        job_type = "Full-time"
        for t in self.filters.get("type", []):
            t_clean = t.lower().replace("-", "").replace(" ", "")
            if t_clean in title_lower.replace("-", "").replace(" ", ""):
                job_type = t
                break
                
        job["Job Level"] = level
        job["Type"] = job_type
        return job

    def _apply_filters(self, jobs):
        filtered = []
        keywords = [k.lower() for k in self.filters.get("keywords", [])]
        requested_levels = [l.lower() for l in self.filters.get("level", [])]
        
        for job in jobs:
            if requested_levels and job["Job Level"].lower() not in requested_levels and job["Job Level"] != "Unknown":
                continue
                
            text_content = (job["Position"] + " " + job["JD"]).lower()
            if keywords and not any(k in text_content for k in keywords):
                continue
                
            filtered.append(job)
        return filtered
