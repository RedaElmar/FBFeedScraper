from selenium import webdriver
import csv
import ast
import datetime
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
# debug mode: doesn't store any data.
# only output the data of the first page
debug = False

# scrape only recent months data or all the history data
onlyRecentData = False

base_url = 'https://mbasic.facebook.com/EducationNationaleMaroc/'
# -------------------------------------------------------------------------
account = 'your username'  ###################################################
password = 'your password'  ##################################################
# -------------------------------------------------------------------------


profile = webdriver.FirefoxProfile()
profile.set_preference("dom.webnotifications.enabled", False)
browser = webdriver.Firefox(options=options, firefox_profile=profile)
browser.get(base_url)

# login
print('----------------------------log in started----------------------------')
browser.get('https://mbasic.facebook.com/')
a = browser.find_element_by_id('m_login_email')
a.send_keys(account)
print("Email Id entered...")
b = browser.find_element_by_name('pass')
b.send_keys(password)
print("Password entered...")
c = browser.find_element_by_name('login')
c.click()
print('----------------------------log in ended----------------------------')

if not debug:
    csvName = input('choose a name for your output csv:') + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    csvFile = open(csvName + '.csv', 'w', newline='', encoding='utf-16')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(
        ['Post ID', 'Time', 'Text', 'Comments', 'Shares', 'All', 'Love', 'Thankful', 'Wow', 'Like', 'Angry', 'Yay',
         'Haha', 'Sad',
         'Post Link'])

articleIDListSum = []
articleTimeListSum = []
articleTextListSum = []
articleLinkListSum = []
totalEmotionsListSum = []
emotionList = ['All', 'Love', 'Thankful', 'Wow', 'Like', 'Angry', 'Yay', 'Haha', 'Sad']

page = 1


def loadPage(page_url):
    global page
    print('------------------------------------------page:', page)
    page += 1

    browser.get(page_url)
    articles = browser.find_elements_by_xpath(
        "//div[@id='structured_composer_async_container']/div/div/section/article")
    print(len(articles), 'articles in this page')
    articleIDList = []
    articleTextList = []
    articleLinkList = []
    totalEmotionsList = []
    articleTimeList = []
    commentList = []
    shareList = []

    for i in range(len(articles)):
        postDicStr = articles[i].get_attribute('data-ft')
        postDic = ast.literal_eval(postDicStr)
        # print('post id is:',postDic["mf_story_key"])
        articleIDList.append(postDic["mf_story_key"])

        curdate = articles[i].find_elements_by_xpath("./footer/div/abbr")
        if len(curdate) == 0:
            articleTimeList.append('time not showing')
        else:
            articleTimeList.append(curdate[0].text)
        # print('post date is :',curdate[0].text)

        ps = articles[i].find_elements_by_xpath("./div/div/span/p")
        strTemp = ''
        for p in ps:
            p.text.replace("\n", " ")
            strTemp += (p.text + ' ')
        articleTextList.append(strTemp)
        # print('post text is :',strTemp)

        bottomColumn = articles[i].find_element_by_xpath("./footer").find_elements_by_xpath("./div")[1]

        commentNum = 0
        try:
            comment = bottomColumn.find_elements_by_xpath("./a")[0].text
            comment: str
            if comment.index('Comment') != 0:
                commentNum = comment[0:comment.index('Comment') - 1]
        except:
            print('not being able to extract comment element')
        commentList.append(commentNum)
        # print('comment', commentNum)

        shareNum = 0
        try:
            share = bottomColumn.find_elements_by_xpath("./a")[1].text
            share: str
            if share.index('Share') != 0:
                shareNum = share[0:share.index('Share') - 1]
        except:
            print('not being able to extract share element')
        shareList.append(shareNum)
        # print('share', shareNum)

        emojiElements = articles[i].find_elements_by_xpath("./footer/div")[1].find_elements_by_xpath("./span/a")
        if len(emojiElements) != 0:
            emojiLinkHref = emojiElements[0].get_attribute('href')
            articleLinkList.append(emojiLinkHref)
        else:
            articleLinkList.append('')

    print('articleIDList length', len(articleIDList))
    print('articleTextList length', len(articleTextList))
    print('-------------begin processing')

    for i in range(len(articleLinkList)):
        # print(articleTextList[i])

        currentEmotionDic = {}
        if articleLinkList[i] != '':
            try:
                browser.get(articleLinkList[i])
                # print('artile link:',articleLinkList[i])
                style1 = browser.find_elements_by_xpath("//div[@role='article']/div/div/div/div/div/a")
                style2 = browser.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div/div/div/a")
                style3 = browser.find_elements_by_xpath("//div[@role='main']/div/div/div/div/div/div/div/div/a")
                if len(style1) != 0:
                    style1[0].click()
                elif len(style2) != 0:
                    style2[0].click()
                else:
                    style3[0].click()
                innerPageEmotionEles = browser.find_elements_by_xpath("//a[@role='button']")
                for innerPageEmotionEle in innerPageEmotionEles:
                    if 'All' in innerPageEmotionEle.text:
                        # emotionSet.add("All")
                        text = innerPageEmotionEle.text
                        text: str
                        subText = text[text.index(' ') + 1:]
                        currentEmotionDic['All'] = subText
                    else:
                        altStr = innerPageEmotionEle.find_element_by_xpath('./img').get_attribute('alt')
                        # emotionSet.add(altStr)
                        num = innerPageEmotionEle.find_element_by_xpath('./span').text
                        currentEmotionDic[altStr] = num
            except Exception as exc:
                print('exception!!! program dies in this post\n', exc)
                # raise
        totalEmotionsList.append(currentEmotionDic)

        # print emoji dic
        print(currentEmotionDic)

    articleIDListSum.extend(articleIDList)
    articleTimeListSum.extend(articleTimeList)
    articleTextListSum.extend(articleTextList)
    articleLinkListSum.extend(articleLinkList)
    totalEmotionsListSum.extend(totalEmotionsList)

    if not debug:
        for i in range(len(articleIDList)):
            rowList = []
            rowList.append(articleIDList[i])
            rowList.append(articleTimeList[i])
            rowList.append(articleTextList[i])
            rowList.append(commentList[i])
            rowList.append(shareList[i])
            for emo in emotionList:
                if emo in totalEmotionsList[i]:
                    rowList.append(totalEmotionsList[i][emo])
                else:
                    rowList.append(0)

            rowList.append(articleLinkList[i])
            print(rowList)
            print('------')
            csvWriter.writerow(rowList)

    browser.get(page_url)
    morePages = browser.find_elements_by_link_text('Show more')
    if not debug and len(morePages) != 0:
        nextPage = morePages[0].get_attribute('href')
        loadPage(nextPage)


if onlyRecentData:
    loadPage(base_url)
else:
    # year data + recent data
    loadPage(base_url)

    # get year list elements
    browser.get(base_url)

    yearsEle = browser.find_elements_by_xpath("//div[@id='structured_composer_async_container']/div[@class='j']")
    print('yearsEle\n', yearsEle)

    links = []
    yearsIdx = []

    # create year list links
    for i in range(len(yearsEle)):
        if i == 0 or i == len(yearsEle) - 1:
            continue
        yearElement = yearsEle[i].find_element_by_tag_name('a')
        links.append(yearElement.get_attribute('href'))
        yearsIdx.append(yearElement.text)
        print(yearElement.text, yearElement.get_attribute('href'))
    cnt = 0
    for i in range(len(links)):
        if cnt > 1:
            break
        cnt += 1
        print('--------------------------  ', yearsIdx[i], '  --------------------------')
        loadPage(links[i])

if not debug:
    # close csv
    csvFile.close()

print('---------------------finally')
print('total posts found', len(articleIDListSum))
