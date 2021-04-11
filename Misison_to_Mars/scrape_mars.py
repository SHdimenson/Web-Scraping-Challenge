# dependencies and setup
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=True)

def soupify(url, browser):

    # visit the website url
    browser.visit(url)
    time.sleep(1)

    # create HTML object
    html = browser.html

    # parse HTML with BeautifulSoup
    soup = bs(html, 'html.parser')
    return soup

def scrape():
    browser = init_browser()
    

    # Navigating Mars News Page------------------------------
    
    MarsNews_url = 'https://mars.nasa.gov/news/'
    soup = soupify(MarsNews_url, browser)

    print("Scraping Mars News...")

    results= soup.find('li', class_="slide")
    news_title = results.find_all('h3')[0].text
    news_para = results.find_all('a')[0].text
    news_date = results.find('div', class_='list_date').text

    print("Mars News: Scraping Complete!")



    
    # Navigating JPL space page for Featured Image----------------------------------------------------
    
    JPLimage_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    soup = soupify(JPLimage_url, browser)
    
    print("Scraping JPL Featured Space Image...")

    # use splinter to click on the 'full image' button to retrieve a full-size jpg url
    browser.find_by_text(' FULL IMAGE').click()
    time.sleep(1)
    
    # get the html for the full featured image
    full_img_html = browser.html

    # parse HTML with BeautifulSoup
    full_img_soup = bs(full_img_html, 'html.parser')

    # find the src for img tag with class 'fancybox-image'
    header_img_url_partial = full_img_soup.find('img', class_='fancybox-image')['src']
    
    # creating the final URL for JPL featured image
    base_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space'
    featured_image_url = base_url + '/' + header_img_url_partial

    # getting the title of the deatured image
    featured_img_title = soup.find('h1',class_='media_feature_title').text
    
    print("Featured Space Image: Scraping Complete!")

    

    #  Navigating Space-Facts Page to scrape Mars-facts table------------------------------------------------------------------------------
    print("Scraping Mars Facts...")

    MarsFacts_url = 'https://space-facts.com/mars/'

    # visit the Mars Facts website
    browser.visit(MarsFacts_url)
    time.sleep(1)

    # create HTML object
    html = browser.html
    
    # use Pandas to scrape table of facts
    table = pd.read_html(html)

    # use indexing to slice the table to a dataframe
    facts_df = table[0]
    facts_df.columns =['Description', 'Value']
    facts_df['Description'] = facts_df['Description'].str.replace(':', '')

    # convert the dataframe to a HTML table and pass parameters for styling
    html_table = facts_df.to_html(index=False, header=True, border=1, justify = 'left',classes="table text-white")

    print("Mars Facts: Scraping Complete!")


    
    #Navigating Astrogeology Page to scrape Mars Hemisphere images---------------------------------------------------------------------
    print("Scraping Hemisphere Images...")
    Hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    soup = soupify(Hemisphere_url, browser)
    
    # retrieve all the parent div tags for each hemisphere
    hemispheres = soup.find_all('div', class_="item")

    # create an empty list to store the python dictionary
    hemisphere_image_data = []

    # loop through each div item to get hemisphere data
    for hemisphere in range(len(hemispheres)):

        # use splinter's browser to click on each hemisphere's link in order to retrieve image data
        hem_link = browser.find_by_css("a.product-item h3")
        hem_link[hemisphere].click()
        time.sleep(1)
    
        # create a beautiful soup object with the image detail page's html
        img_detail_html = browser.html
        imagesoup = bs(img_detail_html, 'html.parser')
    
        # create the base url for the fullsize image link
        base_url = 'https://astrogeology.usgs.gov'
    
        # retrieve the full-res image url and save into a variable
        hem_url = imagesoup.find('img', class_="wide-image")['src']
    
        # complete the featured image url by adding the base url
        img_url = base_url + hem_url

        # retrieve the image title using the title class and save into variable
        img_title = browser.find_by_css('.title').text
    
        # add the key value pairs to python dictionary and append to the list
        hemisphere_image_data.append({"title": img_title, "img_url": img_url})
    
        # go back to the main page 
        browser.back()

    # Quit the browser after scraping
    browser.quit()

    print("Hemisphere Images: Scraping Complete!")
    
    
    #Store all values in dictionary==================================================================
    scraped_mars = {
        "news_title": news_title,
        "news_date": news_date,
        "news_para": news_para,
        "featured_image_title": featured_img_title,
        "featured_image_url": featured_image_url,
        "mars_fact_table": html_table, 
        "hemisphere_images": hemisphere_image_data
    }

    # Return the dictionary of results
    return scraped_mars
