# G2Crowd Crawler

This mini project is about scraping G2Crowd companies given a CSV with URLs of the companies. A script has been written to perform this task, using Playwright to emulate a browser and avoid captchas.

## Execution

To make the execution easy, a Dockerfile is provided to build and run the crawler.

### Build the Docker Image

To build the Docker image, run the following command in your terminal:

```bash
docker build -t g2crowd-crawler .
```

Run the Crawler

To run the crawler, you need to provide a `companies.csv` file containing the URLs of the companies.

Replace `<path_to_company_csv>` with the actual path to your `companies.csv` file

```bash
docker run -v <path_to_company_csv>:/app/companies.csv g2crowd-crawler
```

Make sure you have Docker installed and running on your machine.


## Notes

- The script uses Playwright to emulate a browser, which helps avoid captchas and scrape the G2Crowd website effectively.
- The crawler will output the scraped data to the console.


### Considerations

Even though the captcha was successfully passed, there is an instant ban imposed by the browser. Therefore, it is necessary to spawn a new browser for every URL that is crawled. Firefox browser has shown better performance in bypassing captchas, but it currently has an [open issue](https://github.com/microsoft/playwright/issues/19114) that prevents clicking the captcha validator. On the other hand, using the Chromium browser with the Firefox context has proven to work effectively.

