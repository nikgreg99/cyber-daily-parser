from bs4 import BeautifulSoup

import os
import html2text
import re


# Utilities methods
def skip_lines(file):
    while True:
        last_pos = file.tell()
        line = file.readline()
        if '##' in line:
            return last_pos


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


def cyber_daily_html_to_text():
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    html_2_text_obj = html2text.HTML2Text()
    html_2_text_obj.ignore_links = True
    for folder in os.listdir(cur_dir):
        if re.match(r'em_*', folder):
            html_filepath = os.path.join(folder, 'index.html')
            text_filepath = os.path.join(folder, 'index_text.txt')
            with open(html_filepath, 'rb') as f:
                f_bytes = f.read()
                f_content = f_bytes.decode('utf8')
                soup = BeautifulSoup(f_content, 'html.parser')
            with open(text_filepath, 'w') as f:
                for line in html_2_text_obj.handle(str(soup)):
                    f.write(line)
                f.seek(0)


def parse_article_section(file):
    last_pos = skip_lines(file)
    file.seek(last_pos)
    print('***  ARTICLES    ***')
    is_not_block_ended = True
    title = ''
    while is_not_block_ended:
        while True:
            line = file.readline()
            is_not_block_ended = False if '## Exploited Vulnerabilities' in line else True
            if not is_not_block_ended or line == '\n':
                break
            title += line
        if not is_not_block_ended:
            break
        title = re.sub('## ', '', title)
        title = re.sub('\n','',title)
        print('Title:', title)
        image_link = read_line_at_new_line(file)
        text = read_line_at_new_line(file)
        text = re.sub('\n','',text)
        print('Text:', text)


# STATUS: OK
def parse_vulnerability_section(file):
    print('***  VULNERABILITY EXPLOIT   ***')
    file.readline()
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
        if len(hits_and_related_products) > 1:
            hits = hits_and_related_products[0]
            num_hits = hits[6:]
            related_products = hits_and_related_products[1].split(',')
            related_products[0] = related_products[0][19:]
        else:
            num_hits = hits_and_related_products[6:]
        print('Hits:', num_hits)
        if related_products:
            print('Related products: ', related_products)


# STATUS: OK
def parse_malware_section(file):
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
        targets = hits_and_targets[1].split(',')
        # Remove \n characters
        replace_pattern_with_empty_string(targets, '\n')
        # Remove text 'Targets: '
        targets[0] = targets[0][10:]
        # Remove text 'Hits: '
        num_hits = hits[6:]
        print('Hits:', num_hits)
        print('Targets: ', targets)


# STATUS: OK
def parse_suspicious_ip_section(file):
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
        # Filter useless words: Here it has been shortcut the phrase First seen on Recorded Future
        first_seen = hits_and_first_seen[1][34:]
        num_hits = hits[6:]
        first_seen = re.sub('\n', '', first_seen)
        print('Hits:', num_hits)
        print('First seen on recorded future: ', first_seen)
        # Read blank line
        file.readline()
