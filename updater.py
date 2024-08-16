import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_url(url, download_path):
    target_file_path = os.path.join(download_path, os.path.basename(url))
    if os.path.exists(target_file_path):
        logger.info(f"File already exists: {target_file_path}")
        return

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            with open(target_file_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded: {url} to {target_file_path}")
        elif response.status_code == 404:
            logger.warning(f"File not found: {url}")
        else:
            logger.error(f"Failed to download {url}: Status code {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")

def download_binance_monthly_data(cm_or_um, symbols, intervals, years, months, download_path):
    if cm_or_um not in ["cm", "um"]:
        logger.error("CM_OR_UM can be only cm or um")
        return

    base_url = f"https://data.binance.vision/data/futures/{cm_or_um}/monthly/klines"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for symbol in symbols:
            for interval in intervals:
                for year in years:
                    for month in months:
                        url = f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{year}-{month}.zip"
                        future = executor.submit(download_url, url, download_path)
                        futures.append(future)

        for future in as_completed(futures):
            future.result()

def download_binance_daily_data(cm_or_um, symbols, intervals, year, month, download_path):
    if cm_or_um not in ["cm", "um"]:
        logger.error("CM_OR_UM can be only cm or um")
        return

    base_url = f"https://data.binance.vision/data/futures/{cm_or_um}/daily/klines"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for symbol in symbols:
            for interval in intervals:
                for day in range(1, 32):
                    url = f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02d}-{day:02d}.zip"
                    future = executor.submit(download_url, url, download_path)
                    futures.append(future)

        for future in as_completed(futures):
            future.result()
