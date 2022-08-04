from gmail_service import search_messages, read_message, gmail_authenticate
from cyber_parser import cyber_daily_html_to_text, parse_malware_section, parse_vulnerability_section,parse_suspicious_ip_section,parse_article_section


def main():
    cyber_daily_html_to_text()
    file = open('em_17/index_text.txt')
    parse_article_section(file)
    parse_vulnerability_section(file)
    parse_malware_section(file)
    parse_suspicious_ip_section(file)


if __name__ == '__main__':
    main()
