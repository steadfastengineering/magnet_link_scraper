
import libtorrent as lt
import time 
import argparse
import concurrent.futures
import os
import shutil
import datetime
import json
import sys
from tqdm import tqdm  

save_path = "./.temp"
meta_data_path = "./metadata"
 
def get_metadata(magnet_link):
    ses = lt.session()
    params = lt.add_torrent_params()
    params.url = magnet_link  
    if not os.path.exists(save_path):
        os.makedirs(save_path) 
    params.save_path = save_path
    params.upload_mode = True 
    handle = ses.add_torrent(params)  
    while handle.torrent_file() is None:
        # Some metadata fetchs quickly while some may take a very long time.  
        time.sleep(1)
      
    status = handle.status()
    return status

def clean_up(quiet=True):
    """
    Delete all files and directories inside the .temp directory.
    """
    if not quiet: 
        print(f"Removing any torrent data found in: {save_path}")
    
    if os.path.exists(save_path):
        for entry in os.listdir(save_path):
            path = os.path.join(save_path, entry)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path) 
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    
            except Exception as e:
                print(f"Failed to delete {path}. Reason: {e}")
    else:
        print(f"Directory {save_path} does not exist. Nothing to clean.")

def dump_metadata(links):
    """
    Fetch metadata for a list of magnet links in parallel using get_metadata().
    Write the result for each magnet link to a shared text file specified by meta_data_path.
    """
    file_name = f"magnetlinks_metadata_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    full_path = os.path.join(meta_data_path, file_name)

    print(f"Fetching metadata to {full_path}")

    link_count = len(links) 
    pbar = tqdm(
        range(link_count),
        file=sys.stdout,
        colour='GREEN',
        desc=f"Fetching metadata: ... ",
        unit='',
        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]"
    )
 
   # Process links sequentially with background thread for each link
    with open(full_path, "w") as f, concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for link in links:
            # Submit the task to the executor
            future = executor.submit(get_metadata, link)
            
            # Poll the future once per second until done
            while not future.done():
                pbar.set_description("Processing...")
                pbar.refresh()
                time.sleep(1)
                
            # Once done, update description and write the result
            try:
                status = future.result()
                result = f"{status.name}, {status.info_hash}, {link}\n"
                pbar.set_description(f"Fetched: {status.info_hash}")
            except Exception as e:
                result = f"Error fetching metadata for link {link}: {e}\n"
                pbar.set_description("Error encountered!")
                
            f.write(result)
            pbar.update(1)
            
    pbar.close()
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve meta data for a given magnet link or a list of magnet links from a file.")
    parser.add_argument("magnet_link", nargs="?", help="A single magnet link in quotes")
    parser.add_argument("--txt", help="Path to a file containing a list of magnet links, one per line")
    parser.add_argument("--json", help="Path to a file containing magnet links storaged as JSON. Eg. [ { magnet: \"<link_text>\"}]")
    args = parser.parse_args()

    if args.txt: 
        # Process all links stored in a plain text document. 
        with open(args.txt, "r") as file:
            links = [line.strip() for line in file if line.strip()]
            dump_metadata(links)
            clean_up(quiet=False)
    elif args.json:
        # Process all links stored in a JSON document.
        with open(args.json, 'r') as file:
            data = json.load(file)
            links = [entry["magnet"] for entry in data if "magnet" in entry]
            dump_metadata(links)
            clean_up(quiet=False)
    elif args.magnet_link:
        # Process a single magnet link
        status = get_metadata(magnet_link=args.magnet_link)
        clean_up(quiet=True)
        print(status.name)
    else:
        parser.print_help()
