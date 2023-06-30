import csv
import logging
import os

from linkedin_navigator import LinkedInNavigator

# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

 
if __name__ == '__main__':
    
    RESULT_DIRECTORY = os.getenv("RESULT_DIRECTORY", default="results")
    result_file = os.path.join(RESULT_DIRECTORY, "urls.csv")
    username = os.getenv("USERNAME", default="")
    password = os.getenv("PASSWORD", default="")

    snb = LinkedInNavigator(username, password)
    
    with open('companies.csv', mode='r') as file, open(result_file, 'w') as result_csv:
        writer = csv.writer(result_csv)
        csv_file = csv.reader(file)
        writer.writerow(["Company", "link", "employees number"])

        for company, in csv_file:
            logger.info("processing %s company", company)
            results = snb.search(company)
            for link in results:
                logger.info("processing company link: %s", link)
                employees_number = snb.get_employees_number(link)
                writer.writerow([company, link, employees_number])
