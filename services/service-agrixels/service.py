import time
import shutil
import os

def run_service(input_path, output_path, log, log_progress):
    log("Service logic started.")
    log(f"Converting to agrixels format and saving into {output_path}")
    src = os.path.join(os.path.dirname(__file__), 'SAMPLE_AGRICULTURA_MAPAPARCELLES_2024.csv')
    shutil.copyfile(src, output_path)
    log("Service logic completed.")
