from bs4 import BeautifulSoup

import os
import html2text
import re

from db_manager import save_article, save_malware, save_podcast, save_supsicious_ip, save_vulnerability


def parse_cyber_daily_newsletter(file_path,cursor):
    newsletter = open(file_path, 'r', encoding='utf-8')
    is_podcast_section, starting_pos = is_podcast_section_present(newsletter)
    if is_podcast_section:
        parse_podcast_section(newsletter, starting_pos,cursor)
    else:
        newsletter.seek(0)
    parse_article_section(newsletter,cursor)
    parse_vulnerability_section(newsletter,cursor)
    parse_malware_section(newsletter,cursor)
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


def replace_pattern_with_empty_string(items, pattern):
    for i in range(len(items)):
        items[i] = re.sub(pattern, '', items[i].rstrip())


def read_line_at_new_line(file):
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
        f.seek(0)
    return text_filepath


def is_podcast_section_present(file):
    last_pos = skip_lines(file, '## Podcast')
    if last_pos > 0:
        return True, last_pos
    return False, 0


def parse_podcast_section(file, last_pos,cursor):
    file.seek(last_pos)
    print('*** PODCAST ***')
    podcast_title = read_line_at_new_line(file)
    podcast_title = re.sub('## Podcast: ','',podcast_title)
    podcast_title = re.sub('\n','',podcast_title)
    print('Podcast title: ', podcast_title)
    read_line_at_new_line(file)
    podcast_text =  read_line_at_new_line(file)
    print('Podcast text: ',podcast_text)
    save_podcast(cursor,podcast_title,podcast_text)


# STATUS: OK
def parse_article_section(file,cursor):
    last_pos = skip_lines(file, '##')
    file.seek(last_pos)
    print('***  ARTICLES    ***')
    is_not_block_ended = True
    while is_not_block_ended:
        title = ''
        while True:
          line = file.readline()
          is_not_block_ended = False if '## Exploited Vulnerabilities' in line else True
          if not is_not_block_ended or line == '\n':
                break
          title += line
        if not is_not_block_ended:
            break
        title = re.sub('## ', '', title)
        title = re.sub('\n', '', title)
        print('Title:', title)
        # Skip image URL
        read_line_at_new_line(file)
        text = read_line_at_new_line(file)
        text = re.sub('\n', '', text)
        print('Text:', text)
        save_article(cursor,title,text)


# STATUS: OK
def parse_vulnerability_section(file,cursor):
    file.readline()
    print('***  VULNERABILITY EXPLOIT   ***')
    is_not_block_ended = True
    # Check if block is ended
    while is_not_block_ended:
        CVE = file.readline()
        CVE = re.sub('\n', '', CVE)
        print('CVE:', CVE)
        # Read blank line
        file.readline()
        hits_and_related_products = ''
        while True:
            line = file.readline()
            is_not_block_ended = False if '## Malware' in line else True
            if not is_not_block_ended or line == "\n":
                break
            hits_and_related_products += line
        # Split hits and related products using the following format: Hits: number | Related products: Product 1, Product 2
        hits_and_related_products = hits_and_related_products.split('|')
        replace_pattern_with_empty_string(hits_and_related_products, '\n')
        # Means that we have both hits and related_products
        related_products = []
        if len(hits_and_related_products) == 2:
            hits = hits_and_related_products[0]
            num_hits = hits[6:]
            related_products = hits_and_related_products[1].split(',')
            related_products[0] = related_products[0][19:]
        else:
            num_hits = hits_and_related_products[0][6:]
        print('Hits:', num_hits)
        print('Related products: ', related_products)
        save_vulnerability(cursor,CVE,num_hits,related_products)


# STATUS: OK
def parse_malware_section(file,cursor):
    print('***  MALWARE   ***')
    # Empty Line
    file.readline()
    is_not_block_ended = True
    while is_not_block_ended:
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
            is_not_block_ended = False if '## Suspicious IP Addresses' in line else True
            if not is_not_block_ended or line == '\n':
                break
            hits_and_targets += line
        # Split hits and target using the following format: Hits: number | Targets Target1, Target2
        hits_and_targets = hits_and_targets.split('|')
        hits = hits_and_targets[0]
        if len(hits_and_targets) == 2:
            targets = hits_and_targets[1].split(',')
            # Remove \n characters
            replace_pattern_with_empty_string(targets, '\n')
            # Remove text 'Targets: '
            targets[0] = targets[0][10:]
            # Remove text 'Hits: '
            num_hits = hits[6:]
        print('Hits:', num_hits)
        print('Targets: ', targets)
        save_malware(cursor,malware,num_hits,targets)


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
        hits_and_first_seen = file.readline().split('|')
        hits = hits_and_first_seen[0]
        # Filter useless words: Here it has been shortcut the string 'First seen on Recorded Future'
        first_time_seen = hits_and_first_seen[1][34:]
         # Filter useless words: Here it has been shortcut the string 'Hits:'
        num_hits = hits[6:]
        first_time_seen = re.sub('\n', '', first_time_seen)
        print('Hits:', num_hits)
        print('First seen on Recorded future: ', first_time_seen)
        save_supsicious_ip(cursor,ip_address,num_hits,first_time_seen)
        # Read blank line
        file.readline()
