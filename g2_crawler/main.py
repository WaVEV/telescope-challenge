from crawler_g2company import G2CompranyCrawl


CSV_FILE = 'companies.csv'


if __name__ == '__main__':
    crawler = G2CompranyCrawl(CSV_FILE)
    for data in crawler.extract_data():
        print(data)
