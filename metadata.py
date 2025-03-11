
import libtorrent as lt
import time 
import argparse
import concurrent.futures
import os
import shutil
import datetime

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
        # Some metadata fetchs quickly while some may take a very long time. No reason to idle quickly.
        time.sleep(2)
      
    status = handle.status()
    return status

def clean_up(quiet=True):
    """
    Delete all files and directories inside the .temp directory.
    """
    if os.path.exists(save_path):
        for entry in os.listdir(save_path):
            path = os.path.join(save_path, entry)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                    if not quiet:
                        print(f"Removed any torrent from: {save_path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    if not quiet: 
                        print(f"Removed any torrent data from: {save_path}")
            except Exception as e:
                print(f"Failed to delete {path}. Reason: {e}")
    else:
        print(f"Directory {save_path} does not exist. Nothing to clean.")

def dump_magnet_link_metadata(links):
    """
    Fetch metadata for a list of magnet links in parallel using get_metadata().
    Write the result for each magnet link to a shared text file specified by meta_data_path.
    """
    file_name = f"file_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    full_path = os.path.join(meta_data_path, file_name)

    print(f"Fetching metadata to {full_path}")

    # Using ThreadPoolExecutor to process magnet links concurrently.
    # TODO: break file into chunks of links for each thread to reduce number of threads 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_link = {executor.submit(get_metadata, link): link for link in links}
        
        # Open the shared file for writing results  
        with open(full_path, "w") as f:
            for future in concurrent.futures.as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    status = future.result()
                except Exception as exc:
                    err_msg = f"{link}: failed with exception: {exc}\n"
                    print(err_msg)
                    f.write(err_msg)
                else: 
                    result = f"{status.name}, {status.info_hash}\n"
                     
                    f.write(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve meta data for a given magnet link or a list of magnet links from a file.")
    parser.add_argument("magnet_link", nargs="?", help="A single magnet link in quotes")
    parser.add_argument("--links_file", help="Path to a file containing a list of magnet links, one per line")
    args = parser.parse_args()

    if args.links_file:
        # Read magnet links from the provided file
        with open(args.links_file, "r") as file:
            links = [line.strip() for line in file if line.strip()]
        dump_magnet_link_metadata(links)
        clean_up(quiet=False)
    elif args.magnet_link:
        # Process a single magnet link
        status = get_metadata(magnet_link=args.magnet_link)
        clean_up(quiet=True)
        print(status.name)
    else:
        parser.print_help()
