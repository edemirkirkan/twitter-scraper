# nmNHebKLz5leG2IY
<h1>Twitter Scraper<h1/>

• Twitter Scraper is developed with Python using Selenium, Pandas, and XPath.<br/>
• The app extracts relevant data fields of the tweets that is written about desired search input by automating the search process and web scraping. <br/>
• Store the scraped tweet data into a csv file, and display them on an HTML page in a desired sorted way. <br/>

You can search anything by changing the value of the variable 'search_term' while calling the main function. <br/><br/>
For each different search term, and thus, distinct datasets program generates distinct csv files and HTML pages by naming them automatically with the name of the search term. <br/><br/>
Don't forget to change the variables 'username' and 'password' according to your valid twitter account to successfully login to twitter and get the proper reults. <br/>
request for startup.csv and request for startup.html are generated according to search term 'request for startup', you can delete those files and update the search term and run the script again for your own use. <br/><br/>
Although all the logic of the program is written with python, huge HTML file, approximately 10000 line, is generated since approximately 1150 tweets are scraped from twitter for the search term 'request for startup'. I just wanna note that the reason behind the huge percentage of HTML in the GitHub language distribution of the repo is automatically generated HTML file. 
