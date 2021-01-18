import csv, datetime, os, webbrowser
import pandas as pd
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions

def get_tweet_data(tweet):
    # Extract data from twitter
    try:
        author = tweet.find_element_by_xpath('.//span').text 
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return
    try:
        timestamp = tweet.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:  # In sponsored contents there is no timestamp
        return
    try:
        respond_text = tweet.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return
    try:
        responded_text = tweet.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return
    try:
        num_reply = tweet.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return
    try:
        num_retweet = tweet.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return
    try:
        num_like = tweet.find_element_by_xpath('.//div[@data-testid="like"]').text
    except NoSuchElementException:  # if unsuccessful just eliminate tweet from the data
        return

    author = author.replace("\n", " ").replace('\r', '')  # eliminate new lines

    # changing the format of date so that it can be more readable
    date = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    new_format = "%Y-%m-%d"
    date.strftime(new_format)

    # merge respond tweet and responded tweet into one data field
    content = respond_text + responded_text
    content = content.replace("\n", " ").replace('\r', '')

    # if there is no like, retweet, or comment to a tweet, store it as 0 instead of empty string
    if not num_reply:
        num_reply = "0"
    if not num_retweet:
        num_retweet = "0"
    if not num_like:
        num_like = "0"

    # return tweet with all of its data fields
    tweet_data = [author, num_retweet, num_like, num_reply, str(date), content]
    return tweet_data

def clean_sort_write_data_into_csv(csv_filename, data):
    # write untouched data to file named dirty_data
    with open('dirty_data.csv', 'w', newline='', encoding='utf-8') as file:
        header = ['Author', 'Retweets', 'Likes', 'Comments', 'Timestamp', 'Content']
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        
    # clean non-integer rows of 'Retweets', 'Likes', 'Comments' columns, write new data to file named cleaned_data
    with open('dirty_data.csv', 'r', newline='', encoding='utf-8') as csvfile, open('cleaned_data.csv', 'w', encoding='utf-8') as out:
        fieldnames = ['Author', 'Retweets', 'Likes', 'Comments', 'Timestamp', 'Content']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        reader = csv.DictReader(csvfile)
        writer.writeheader()
        for row in reader:
            try:
                int(row['Retweets']) 
                int(row['Likes']) 
                int(row['Comments'])
                writer.writerow(row)
            except ValueError:
                continue
                
    # read the clean data, sort it, and write it to output csv file
    with open('cleaned_data.csv', newline='', encoding='utf-8') as csvfile, open(csv_filename, 'w', encoding='utf-8') as f:
        reader = csv.DictReader(csvfile)
           
        sortedlist = sorted(reader, key=lambda row:(int(row['Retweets']),int(row['Likes']),int(row['Comments'])), reverse=True)

        fieldnames = ['Author', 'Retweets', 'Likes', 'Comments', 'Timestamp', 'Content']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)
            
    # delete the uncleaned and unsorted data
    os.remove('dirty_data.csv')
    os.remove('cleaned_data.csv')

def generate_and_open_HTML(csv_filename, html_filename):
    # uniform the style
    pd.set_option('display.width', 1000)
    pd.set_option('colheader_justify', 'center')

    # create pandas DataFrame object from the data of csv file
    data_frame = pd.read_csv(csv_filename)

    # create string of the HTML table 
    table = data_frame.to_html(classes='mystyle')

    # merge it with the necesarry HTML tags
    html_string = f'''
    <html>
    <head>
        <title>Twitter Scraper</title>
    </head>
    <link rel="stylesheet" type="text/css" href="df_style.css"/>
    <body>
        {table}
    </body>
    </html>.
    '''
    
    # generate the HTML file, write the data from data frame to HTML file
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(html_string)

    # open the HTML page with a proper URL
    path = os.path.abspath(html_filename)
    url = 'file://' + path
    webbrowser.open(url)


def main(username, password, search_term="request for startup"):
    # automation process is described below

    # opening browser
    options = EdgeOptions()
    options.use_chromium = True
    driver = Edge(options=options)

    # navigate twitter login page and make it fullscreen to be able to get access all the elements on the page, and thus, to avoid "NoSuchElementException"
    driver.get("https://twitter.com/login")
    driver.maximize_window()

    # type username
    login_username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
    login_username.send_keys(username)

    # type password
    login_password = driver.find_element_by_xpath('//input[@name="session[password]"]')
    login_password.send_keys(password)

    # login
    login_password.send_keys(Keys.RETURN)

    # search for "request for startup", alternatively you can pass any other term into main function
    search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)

    # navigate the latest tab to get the most recent tweets
    sleep(2)
    driver.find_element_by_link_text('Latest').click()

    data = []
    tweet_ids = set()  # create unique tweet id's to avoid duplicate tweets
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    # keep scrolling until all of the tweets about the topic are being recorded in the Latest tab
    while scrolling:
        tweets = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for tweet in tweets:
            tweet_data = get_tweet_data(tweet)
            if (tweet_data):
                tweet_id = ''.join(tweet_data)
                if (tweet_id not in tweet_ids):
                    tweet_ids.add(tweet_id) # provide uniqueness of tweet ids by concenating them 
                    data.append(tweet_data)
        """
        due to slow internet connection, last_position and current_position can be equal
        and this causes immidiate stop of the program, hence keep the number of scroll attempts 
        to avoid it, and wait for the connection through sleep statements
        """
        scroll_attempt = 0
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(1) # wa
            current_position = driver.execute_script("return window.pageYOffset;")
            if (last_position == current_position):
                scroll_attempt += 1

                if (scroll_attempt >= 3):
                    scrolling = False
                    break
                else:
                    sleep(2)
            else:
                last_position = current_position
                break
                
    # after we obtain all the data, close the browser
    driver.quit()

    # give a unique name to a output of each distinct searches, datasets
    csv_filename = search_term + ".csv"
    html_filename = search_term + ".html"
    
    # store all the data in csv file and display in html page
    clean_sort_write_data_into_csv(csv_filename, data)
    generate_and_open_HTML(csv_filename, html_filename)


if __name__ == "__main__":
    # enter a valid twitter account to obtain the data
    username = "username@gmail.com"  # Username, e-mail, phone number
    password = "************"  # Password
   
    # you can obtain data about any kind of topic by passing this variable to main function
    search_term = "any kind of topic"

    main(username, password)
