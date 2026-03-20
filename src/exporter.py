import logging
import pandas as pd
from datetime import datetime

class ExcelExporter:
    @staticmethod
    def export(jobs, output_file=None):
        if not output_file:
            output_file = f"job_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
        if not jobs:
            logging.warning("No jobs to export.")
            return output_file
            
        df = pd.DataFrame(jobs)
        cols = ["Position", "Job Level", "Company", "Link to Apply", "JD", "Key Notice", "Expiry Date", "Source", "Status"]
        
        for c in cols:
            if c not in df.columns:
                if c == "Status":
                    df[c] = "Not Yet Applied"
                else:
                    df[c] = ""
                    
        df = df[cols]
        df.to_excel(output_file, index=False, engine="openpyxl")
        logging.info(f"Exported {len(df)} jobs to {output_file}")
        print(output_file)
        return output_file
