from playwright.sync_api import sync_playwright,playwright,expect
import pandas as pd
import time
from datetime import datetime


# fill in 
# 1. user profile name, 
# 2. display name 
# 3. start-end date
# 4. your email,password and username
# fill in proxy if any
# recommended to run not more than 6 months time frame for less frequent poster, 3 months for frequent poster
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(proxy = {
            "server":"",
            "username":"",
            "password":""  
        },headless=False) # fill in proxy if needed else remove
        context = browser.new_context()
        profiles = ["johnscharts"] # fill in the user profile name
        texts = ["Johns Charts"] # fill in user display name
        for i,profile in enumerate(profiles):
            scrape_tweet(profile,context,texts[i])
        browser.close()

def scrape_tweet(profile:str,context,text:str):
    user = '' # fill in email
    pw = '' # fill in password
    verification = 'BarberParadoxes' # fill in username
    date_start = "2022-05-01" # fill in start date (older date)
    date_end = '2022-09-01' # fill in end date (recent date)
    # Log in
    page = context.new_page()
    print("Accessing  profile: ",profile)
    page.goto(f"https://twitter.com/search?q=from%3A{profile}%20since%3A{date_start}%20until%3A{date_end}&src=typed_query&f=live",timeout = 800000)
    expect(page.get_by_text("Phone, email, or username")).to_be_visible(timeout=30000)
    page.get_by_text("Phone, email, or username").fill(user)
    page.get_by_text('Next').click()
    
    expect(page.get_by_text("Phone or username").or_(page.get_by_text('Password',exact=True))).to_be_visible(timeout=30000)
    if page.get_by_text("Phone or username").is_visible():
        page.get_by_text("Phone or username").fill(verification)
        page.get_by_text('Next').click()
    page.get_by_text('Password',exact=True).fill(pw)
    page.get_by_role('button',name="Log in").click()
    # scraping
    date_collection = []
    col = []
    temp_len = 0
    stop_counter = 0
    page.locator('article').filter(has_text=text).nth(0).locator("time").nth(0).click()
    page.go_back()
    page.mouse.wheel(0,500)
    while stop_counter<5:
        tweet_locator = page.locator('article').filter(has_text=text)
        tweet_count = tweet_locator.count()
        for y in range(tweet_count):
            expect(tweet_locator.nth(y).locator('time').nth(0)).to_be_visible(timeout=30000)
            date = tweet_locator.nth(y).locator('time').nth(0).get_attribute('datetime')
            if date in date_collection:
                continue
            if tweet_locator.nth(y).get_by_test_id("tweetText").nth(0).is_visible():
                tweet = tweet_locator.nth(y).get_by_test_id("tweetText").nth(0).text_content()
            else:
                tweet=""
            comments_no = tweet_locator.nth(y).get_by_test_id("reply").text_content()
            retweet_no = tweet_locator.nth(y).get_by_test_id("retweet").text_content()
            like_no = tweet_locator.nth(y).get_by_test_id("like").text_content()
            date_collection.append(date)
            article = tweet_locator.nth(y).text_content()

            print(date,len(date_collection))
            if "Show more" in article:
                tweet_locator.nth(y).locator("time").nth(0).click()
                # expect(page.get_by_test_id("tweetText").nth(0)).to_be_visible(80000)
                tweet = page.get_by_test_id("tweetText").nth(0).text_content()
                page.go_back()
                col.append([tweet,date,comments_no,retweet_no,like_no])
                continue
            col.append([tweet,date,comments_no,retweet_no,like_no])
        # stop condition
        if temp_len==len(col):
            stop_counter += 1
        else:
            stop_counter = 0
        temp_len=len(col)
        print("........................................scrolling.............................................")
        for x in range(10):
            page.mouse.wheel(0,300)
            time.sleep(1)
    df = pd.DataFrame(col,columns = ["tweet","date","comments_no","retweet_no","like_no"])
    df.drop_duplicates(inplace=True)
    df.to_csv(f"tweet_{profile}_{date_start}-{date_end}.csv")

main()
