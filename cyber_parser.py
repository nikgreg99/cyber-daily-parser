from bs4 import BeautifulSoup

import os
import html2text
import re

from db_manager import save_article, save_malware, save_podcast, save_suspicious_ip, save_vulnerability


def parse_cyber_daily_newsletter(file_path,cursor):
    newsletter = open(file_path, 'r', encoding='utf-8')
    is_podcast, starting_pos = is_podcast_section(newsletter)
    if is_podcast:
        parse_podcast(newsletter, starting_pos,cursor)
    else:
        newsletter.seek(0)
    parse_article(newsletter,cursor)
    parse_exploited_vulnerability(newsletter,cursor)
    parse_malware(newsletter,cursor)
    parse_suspicious_ip_section(newsletter,cursor)


# Utility method
def skip_lines(file, pattern):
    while True:
        last_pos = file.tell()
        line = file.readline()
        if pattern in line:
            return last_pos
        if not line:
            return 0


def replace_with_empty_string(items, pattern):
    for i in range(len(items)):
        items[i] = re.sub(pattern, '', items[i].rstrip())


def read_file_at_(file):
    content = ''
    while file:
        line = file.readline()
        if line == '\n':
            break
        content += line
    return content


def cyber_daily_html_to_text(folder):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(cur_dir, folder)
    html_to_text_obj = html2text.HTML2Text()
    html_to_text_obj.ignore_links = True
    html_filepath = os.path.join(folder_path, 'index.html')
    text_filepath = os.path.join(folder_path, 'index_text.txt')
    with open(html_filepath, 'rb') as f:
        f_bytes = f.read()
        f_content = f_bytes.decode('utf8')
        soup = BeautifulSoup(f_content, 'html.parser')
    with open(text_filepath, 'w', encoding='utf-8') as f:
        for line in html_to_text_obj.handle(str(soup)):
            f.write(line)
    return text_filepath


def is_podcast_section(file):
    last_pos = skip_lines(file, '## Podcast')
    if last_pos > 0:
        return True, last_pos
    return False, 0

# STATUS: OK
def parse_podcast(file, last_pos,cursor):
    #Here a for loop wasn't used cause a podcast may appear once (not always)
    file.seek(last_pos)
    print('*** PODCAST ***')
    podcast_title = read_file_at_(file)
    podcast_title = re.sub('## Podcast: ','',podcast_title)
    podcast_title = re.sub('\n','',podcast_title)
    print('Podcast title: ', podcast_title)
    read_file_at_(file)
    podcast_text =  read_file_at_(file)
    print('Podcast text: ',podcast_text)
    save_podcast(cursor,podcast_title,podcast_text)


# STATUS: OK
def parse_article(file,cursor):
    last_pos = skip_lines(file, '##')
    file.seek(last_pos)
    print('***  ARTICLES    ***')
    is_not_ended = True
    while is_not_ended:
        title = ''
        while True:
          line = file.readline()
          is_not_ended = False if '## Exploited Vulnerabilities' in line else True
          if not is_not_ended or line == '\n':
                break
          title += line
        if not is_not_ended:
            break
        title = re.sub('## ', '', title)
        title = re.sub('\n', '', title)
        print('Title:', title)
        # Skip image URL (not particulary relevant)
        read_file_at_(file)
        text = read_file_at_(file)
        text = re.sub('\n', '', text)
        print('Text:', text)
        save_article(cursor,title,text)


# STATUS: OK
def parse_exploited_vulnerability(file,cursor):
    file.readline()
    print('***  VULNERABILITY EXPLOIT   ***')
    is_not_end = True
    # Check if block is ended
    while is_not_end:
        cve = file.readline()
        cve = re.sub('\n', '', cve)
        print('CVE:', cve)
        # Read blank line
        file.readline()
        hits_and_products = ''
        while True:
            line = file.readline()
            is_not_end = False if '## Malware' in line else True
            if not is_not_end or line == "\n":
                break
            hits_and_products += line
        if '|' in hits_and_products: 
            # Split hits and products using the following format: Hits: number | Related products: Product 1, Product 2
            hits, products = hits_and_products.split('|')
            num_hits = hits[6:]
            product_list = products.split(',')
            product_list[0] = product_list[0][19:]
            replace_with_empty_string(product_list, '\n')
        else:
            num_hits = hits_and_products[6:]
            #Workaround for inserting always a list, also when there aren't related products 
            product_list = []
        print('Hits:', num_hits)
        if product_list:
            print('Products: ', product_list)
        save_vulnerability(cursor,cve,num_hits,product_list)


# STATUS: OK
def parse_malware(file,cursor):
    print('***  MALWARE   ***')
    # Empty Line
    file.readline()
    is_not_end = True
    while is_not_end:
        # Malware name
        malware = file.readline()
        malware = re.sub('\n', '', malware)
        print('Malware:', malware)
        # Empty Line
        file.readline()
        hits_and_targets = ''
        while True:
            line = file.readline()
            # Check for Malware section ending
            is_not_end = False if '## Suspicious IP Addresses' in line else True
            if not is_not_end or line == '\n':
                break
            hits_and_targets += line
        # Split hits and target using the following format: Hits: number | Targets Target1, Target2
        if '|' in hits_and_targets:
            hits, targets = hits_and_targets.split('|')
            num_hits = hits[6:]
            target_list = targets.split(',')
            target_list[0] = target_list[0][10:]
            # Remove \n characters
            replace_with_empty_string(target_list, '\n')
        else:
            num_hits = hits_and_targets[6:]
            target_list = []
        print('Hits:', num_hits)
        if target_list:
            print('Targets: ', target_list)
        save_malware(cursor,malware,num_hits,target_list)


# STATUS: OK
def parse_suspicious_ip_section(file,cursor):
    print('***  SUSPICIOUS IP ADDRESSES   ***')
    # Read blank line
    file.readline()
    while True:
        ip_address = file.readline()
        # IP Address section terminator
        if ip_address == "| | |  \n":
            break
        # Restyling IP Address using its own format
        ip_address = re.sub('\[.\]', '.', ip_address)
        ip_address = re.sub('\n', '', ip_address)
        print('IP Address:', ip_address)
        # Read blank line
        file.readline()
        # Splits hits and first seen information using the following format: Hits: number | First seen on Recorded Future: Date
        hits, first_seen = file.readline().split('|')
        # Filter useless words: Here it has been shortcut the string 'Hits:'
        num_hits = hits[6:]
        # Filter useless words: Here it has been shortcut the string 'First seen on Recorded Future'
        first_seen = first_seen[34:]
        first_seen = re.sub('\n', '', first_seen)
        print('Hits:', num_hits)
        print('First seen on Recorded future: ', first_seen)
        save_suspicious_ip(cursor,ip_address,num_hits,first_seen)
        # Read blank line
        file.readline()
