# Disclaimer:
# This code/script/application/program is solely for educational and learning purposes.
# All information, datasets, images, code, and materials are presented in good faith and
# intended for instructive use. However, noarche make no representation or warranty, 
# express or implied, regarding the accuracy, adequacy, validity, reliability, availability,
# or completeness of any data or associated materials.
# Under no circumstance shall noarche have any liability to you for any loss, damage, or 
# misinterpretation arising due to the use of or reliance on the provided data. Your utilization
# of the code and your interpretations thereof are undertaken at your own discretion and risk.
#
# By executing script/code/application, the user acknowledges and agrees that they have read, 
# understood, and accepted the terms and conditions (or any other relevant documentation or 
#policy) as provided by noarche.
#
#Visit https://github.com/noarche for more information. 
#
#  _.··._.·°°°·.°·..·°¯°·._.··._.·°¯°·.·° .·°°°°·.·°·._.··._
# ███╗   ██╗ ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗███████╗
# ████╗  ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝
# ██╔██╗ ██║██║   ██║███████║██████╔╝██║     ███████║█████╗  
# ██║╚██╗██║██║   ██║██╔══██║██╔══██╗██║     ██╔══██║██╔══╝  
# ██║ ╚████║╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║███████╗
# ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝
# °°°·._.··._.·°°°·.°·..·°¯°··°¯°·.·°.·°°°°·.·°·._.··._.·°°°

import os
import requests
import threading
import socket
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

    # Ask the user for the website names (comma-separated)
    website_names_input = input("Enter the website names (e.g., yahoo,google,bing): ").strip()
    website_names = [name.strip() for name in website_names_input.split(',')]

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

    # Function to check if a website is online and valid
    def check_website(website_name, pbar):
        for gtld in gtlds:
            url = f"https://{website_name}.{gtld}"
            try:
                # Resolve the IPv4 address
                ipv4 = socket.gethostbyname(f"{website_name}.{gtld}")

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
                                    print(f"{Fore.GREEN}{ipv4} | {bandwidth_used:.2f}KB | {url} | {safe_title}")
                                    with open(responsive_links_path, 'a', encoding='utf-8') as responsive_file:
                                        responsive_file.write(f"{ipv4},{bandwidth_used:.2f}KB,{url},{safe_title}\n")
                    else:
                        with threading.Lock():
                            print(f"{Fore.GREEN}{ipv4} | {bandwidth_used:.2f}KB | {url} | {safe_title}")
                            with open(responsive_links_path, 'a', encoding='utf-8') as responsive_file:
                                responsive_file.write(f"{ipv4},{bandwidth_used:.2f}KB,{url},{safe_title}\n")
            except (requests.RequestException, socket.gaierror):
                pass
            pbar.update(1)

    for website_name in website_names:
        print(f"{Fore.YELLOW}Checking {website_name}...{Style.RESET_ALL}")
        
        # Initialize progress bar
        with tqdm(total=len(gtlds), desc=f"{Fore.CYAN}Checking {website_name}", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]", colour='cyan') as pbar:
            # Create and start threads
            threads = []
            for _ in range(num_threads):
                thread = threading.Thread(target=check_website, args=(website_name, pbar))
                thread.start()
                threads.append(thread)

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

    print(f"{Fore.YELLOW}Finished checking all websites.{Style.RESET_ALL}")

    # Ask the user if they want to run the script again
    run_again = input("Do you want to check another set of websites? (yes/y or no/n) [default: no]: ").strip().lower()
    if run_again not in ['yes', 'y']:
        print(f"{Fore.RED}Exiting...{Style.RESET_ALL}")
        break


# Disclaimer:
# This code/script/application/program is solely for educational and learning purposes.
# All information, datasets, images, code, and materials are presented in good faith and
# intended for instructive use. However, noarche make no representation or warranty, 
# express or implied, regarding the accuracy, adequacy, validity, reliability, availability,
# or completeness of any data or associated materials.
# Under no circumstance shall noarche have any liability to you for any loss, damage, or 
# misinterpretation arising due to the use of or reliance on the provided data. Your utilization
# of the code and your interpretations thereof are undertaken at your own discretion and risk.
#
# By executing script/code/application, the user acknowledges and agrees that they have read, 
# understood, and accepted the terms and conditions (or any other relevant documentation or 
#policy) as provided by noarche.
#
#Visit https://github.com/noarche for more information. 
#
#  _.··._.·°°°·.°·..·°¯°·._.··._.·°¯°·.·° .·°°°°·.·°·._.··._
# ███╗   ██╗ ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗███████╗
# ████╗  ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝
# ██╔██╗ ██║██║   ██║███████║██████╔╝██║     ███████║█████╗  
# ██║╚██╗██║██║   ██║██╔══██║██╔══██╗██║     ██╔══██║██╔══╝  
# ██║ ╚████║╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║███████╗
# ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝
# °°°·._.··._.·°°°·.°·..·°¯°··°¯°·.·°.·°°°°·.·°·._.··._.·°°°