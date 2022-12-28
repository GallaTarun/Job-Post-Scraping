import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

JOBS_INFO = []

URL = 'https://www.naukri.com/allcompanies?searchType=premiumLogo&title=Featured+companies+actively+hiring&branding=%257B%2522pagename%2522%253A%2522ni-desktop-premium-viewAll%2522%257D&pageNo=1&qcount=47'
driver = webdriver.Chrome()

def get_jobs_list(job_page_url):
    driver.get(job_page_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # <article> .jobtuple -> for entire job post
    job_posts_div = soup.find("div", attrs={"class": "parentContainer"})

    if job_posts_div:
        job_posts = job_posts_div.findChildren("article", recursive=False)

        for post in job_posts:
            job_title_tag = post.find("a", attrs={"class": "title"})
            if job_title_tag:
                job_title = job_title_tag['title']
            else:
                job_title = ""
            
            company_title_tag = post.find("a", attrs={'class': "subTitle"})
            if company_title_tag:
                company_title = company_title_tag['title']
            else:
                company_title = ""

            req_experience_tag = post.find("span", attrs={'class': "ellipsis fleft fs12 lh16"})
            if req_experience_tag:
                req_experience = req_experience_tag['title']
            else:
                req_experience = ""

            salary_span_tag = post.find("span", attrs={'data-test': 'salary'})
            if salary_span_tag:
                salary = salary_span_tag['title']
            else:
                salary = ""

            location_span_tag = post.find("span", attrs={'data-test': 'location'})
            if location_span_tag:
                location = location_span_tag['title']
            else:
                location = ""

            job_description_tag = post.find("div", attrs={'class': "job-description"})
            if job_description_tag:
                job_description = job_description_tag.div.contents[0]
            else:
                job_description = ""

            job_url_tag = post.find("a", attrs={'data-test': 'tupleTitle'})
            if job_url_tag:
                url = job_url_tag['href']
            else:
                url = ""

            JOBS_INFO.append([company_title, job_title, job_description, url, req_experience, salary, location])

def parse_company_jobs_page(company_url):
    driver.get(company_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pagination_div = soup.find('div', attrs={'class': 'paginationDesc'})
    # total number of pages for jobs in this company
    if pagination_div:
        num_pages = int(pagination_div.span['title'].split(' ')[-1])
        
        for page in range(1, num_pages+1):
            get_jobs_list(company_url + '&pageNo=' + str(page))

def list_companies(soup):
    companies_container = soup.find("div", {'class': 'standardTupleContainer'})
    companies_div = companies_container.find_all("div", {"class": "tuple"})
    for company_div in companies_div:
        a_tag = company_div.find("a", {"class": 'cta'})
        parse_company_jobs_page(a_tag['href'])

# def write_to_csv(path):
    # with open(path, 'a') as f:
    #     for info in JOBS_INFO:
    #         f.write(", ".join(info)+"\n")
    # f.close()

def write_to_excel(path):
    df = pd.DataFrame(data= JOBS_INFO, columns=['Company', "Job Title", "Job Description", "Job URL", "Required Experience", "Salary", "Location"])
    df.to_excel(path, sheet_name="Naukri Job openings")

def main():
    driver.get(URL)
    soup = BeautifulSoup(driver.page_source, 'html.parser')   
    list_companies(soup=soup)

    write_to_excel('jobs_list.xlsx')

main()