import json
import os
import gzip


class fileSaver:
    def save_job(date_of_extraction, file_content, company, job_id):
        location = f"job-extractor/jobs/{date_of_extraction}/{company}"
        file_name = f"{company}_{job_id}.json"
        if not os.path.exists(location):
            try:
                os.makedirs(location)
                print(f"Directory '{location}' created successfully.")
            except PermissionError:
                print(f"Permission denied: Unable to create '{location}'.")
                return False
            except Exception as e:
                print(f"An error occurred while creating directory '{location}': {e}")
                return False

        try:
            with gzip.open(f"{location}/{file_name}.gz", "wt", encoding="utf-8") as zipfile:
                json.dumps(file_content, zipfile, ensure_ascii=False, indent=4)
                return True
        except PermissionError:
                print(f"Permission denied: Unable to create '{location}/{file_name}'.")
                return False
        except Exception as e:
                print(f"An error occurred while saving file '{location}/{file_name}': {e}")
                return False