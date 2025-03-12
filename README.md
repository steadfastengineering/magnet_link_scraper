
# Magnet Scraper

This repository contains Python scripts for scraping torrent magnet links from HTML content. It uses modules such as Scrapy and BeautifulSoup to parse web pages and extract magnet links.

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

## Setup

1. **Clone the Repository**
   
   Clone this repository to your local machine:
   ```bash
   git clone <repository-url>
   cd magnet-scraper
   ```

2. **Create a Virtual Environment**

   Create a virtual environment and activate it:
   - On macOS and Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Dependencies**

   Install all required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Scraping Magnet Links

This script uses Scrapy to start crawling from a given URL and extracts magnet links.

- **Script:** `scrape-magnet-links.py`
- **Usage:**
  ```bash
  python scrape-magnet-links.py <start_url>
  ```
  The script creates a JSON file with the scraped magnet links stored in a `links` directory. The filenames are timestamped.

### 2. Fetching Metadata for Magnet links

- **Script:** `metadata.py`
- **Usage:**
  ```bash
  python metadata.py --json <path_to_json>
  ```
  ```bash
  python metadata.py --txt <path_to_txt>
  ```
  ```bash
  python metadata.py <magnet_link>
  ```
  The script fetches the metadata of the supplied magnet link or links and stores the torrent name and hash into a timestamped file in the `metadata` directory.

## Additional Information

- You can customize the script settings (e.g., feed export format) by modifying the settings dictionary in `scrape-magnet-links.py`.
- You may also adjust the metadata which is written to file by `metadata.py`, see libtorrent documentation for more info.  


## Magnet Link JSON Sample
```json
[
{"magnet": "magnet:?<sample_magnet_link>"},
{"magnet": "magnet:?<sample_magnet_link>"}
]
```

## License

MIT License

Happy scraping!
