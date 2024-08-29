import os
import requests
import threading
from queue import Queue
from tqdm import tqdm
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

# Initialize colorama
init(autoreset=True)

while True:
    # Create hits directory if it doesn't exist
    os.makedirs('hits', exist_ok=True)

    # Path to the file where responsive links will be saved
    responsive_links_path = os.path.join('hits', 'responsive_links.txt')

    # Keywords that invalidate a website (as substrings)
    invalid_keywords = ['lander', 'sale', 'available', 'parked domain', 'geparkeerd', 'defecto', 'construction', 'Loading...', 'Domain', 'Registered']

    # Ask the user for the website name
    website_name = input("Enter the website name (e.g., yahoo): ").strip()

    # Ask the user if they want to use the keyword filter (default to yes)
    use_filter_input = input("Do you want to use the keyword filter? (yes/y or no/n) [default: yes]: ").strip().lower()
    use_filter = use_filter_input in ['', 'yes', 'y']

    # Ask the user for the number of threads (default to 10)
    threads_input = input("Enter the number of threads (default: 10): ").strip()
    num_threads = int(threads_input) if threads_input.isdigit() else 10

    # Path to the list of GTLDs
    list_path = 'list.txt'

    # Read the GTLDs from the list file
    with open(list_path, 'r') as file:
        gtlds = [line.strip() for line in file]

    # Queue to manage the GTLDs to be processed by threads
    queue = Queue()

    # Function to check if a website is online and valid
    def check_website(pbar):
        while not queue.empty():
            gtld = queue.get()
            url = f"https://{website_name}.{gtld}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    # Calculate bandwidth used in KB
                    bandwidth_used = len(response.content) / 1024  # Convert to KB

                    # Extract the title from the HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.string.strip() if title_tag else 'No Title'

                    # Remove non-ASCII characters from the title
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')

                    if use_filter:
                        # Apply the filter: skip websites with bandwidth < 2.80 KB
                        if bandwidth_used >= 2.81:
                            # Check for invalid substrings in the response content
                            page_content = response.text
                            for keyword in invalid_keywords:
                                if keyword in page_content:
                                    break
                            else:
                                with threading.Lock():
                                    print(f"{Fore.GREEN}{bandwidth_used:.2f}KB {url} {safe_title}")
                                    with open(responsive_links_path, 'a', encoding='utf-8') as responsive_file:
                                        responsive_file.write(f"{bandwidth_used:.2f}KB,{url},{safe_title}\n")
                    else:
                        with threading.Lock():
                            print(f"{Fore.GREEN}{bandwidth_used:.2f}KB {url} {safe_title}")
                            with open(responsive_links_path, 'a', encoding='utf-8') as responsive_file:
                                responsive_file.write(f"{bandwidth_used:.2f}KB,{url},{safe_title}\n")
            except requests.RequestException:
                pass
            pbar.update(1)
            queue.task_done()

    # Enqueue all GTLDs
    for gtld in gtlds:
        queue.put(gtld)

    # Initialize progress bar
    with tqdm(total=len(gtlds), desc=f"{Fore.CYAN}Checking websites", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]", colour='cyan') as pbar:
        # Create and start threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=check_website, args=(pbar,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        queue.join()

        for thread in threads:
            thread.join()

    print(f"{Fore.YELLOW}Finished checking websites.{Style.RESET_ALL}")

    # Ask the user if they want to run the script again
    run_again = input("Do you want to check another website? (yes/y or no/n) [default: no]: ").strip().lower()
    if run_again not in ['yes', 'y']:
        print(f"{Fore.RED}Exiting...{Style.RESET_ALL}")
        break
