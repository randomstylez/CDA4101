import requests
import time
from bs4 import BeautifulSoup
from mpi4py import MPI

class scoredUrl:
    def __init__(self, url, score):
        self.url = url
        self.score = score
        self.articleArray = self.getAsArray(url)

    def getAsArray(self, url):
        response = requests.get(url)
        responseText = response.text.encode('UTF-8')
        soup = BeautifulSoup(response.text, "html.parser")
        s = soup.find_all('p')
        string1 = str(s)
        arrayS = string1.split(' ')
        arrayS = [word.replace('<p', '').replace('</p>', '').replace('<code>', '').replace('</code>', '')
            .replace('class=', '').replace('href=', '').replace('>', '').replace('<p', '')
            .replace('\"', '').replace('\"', '').replace(',','') for word in arrayS]
        arrayS = list(filter(None, arrayS))
        return arrayS
    
    def getUrl(self):
        return self.url

    def getScore(self):
        return self.score

    def getList(self):
        return self.articleArray

def compare(firstArticle, secondArticle):
    totalCounter = float(len(secondArticle))
    matchCounter = 0.0
    for i in firstArticle:
        for j in secondArticle:
            if j == i:
                matchCounter = matchCounter + 1
    return matchCounter / totalCounter

def listComparison(userArray, listOfArticles, cpu):
    firstMostSimilar = 0
    firstMostName = None 
    secondMostSimilar = 0
    secondMostName = None

    for i in listOfArticles:
        n = compare(userArray, i.getList())
        if n > firstMostSimilar:
            if firstMostSimilar > secondMostSimilar:
                secondMostSimilar = firstMostSimilar
                secondMostName = firstMostName
            firstMostSimilar = n
            firstMostName = i
        print("Article ", listOfArticles.index(i) + 1, "From CPU",cpu,"is", n, "% similar")
	if secondMostName == None:
	    secondMostName = firstMostName
    averageScore = (firstMostName.getScore() + secondMostName.getScore()) / 2
    #print("User article average rating of:",averageScore)
    return averageScore

def starttime():
    return time.time()

def endtime():
    return time.time()

def mpi():
    if cpu == 0:
        for slave in range(1, numcpus):
            comm.send(articleList[slave*numeach:(2*slave*numeach)], dest=slave)

	masterAverage = listComparison(arrayS, articleList[0:(numeach)], cpu) 
	
	totalFromSlaves = masterAverage
        for slave in range(1, numcpus):
	    receivedValue = comm.recv(source=slave)    
	    totalFromSlaves = totalFromSlaves + receivedValue

	totalAverage = totalFromSlaves / comm.Get_size()
	print("Total Average", totalAverage) 
    else:
        slaveList = comm.recv(source=0)

	slaveAverage = listComparison(arrayS, slaveList, cpu)

	comm.send(slaveAverage, dest=0)    


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    cpu = comm.Get_rank()
    numcpus = comm.Get_size()
    #print(numcpus)	
    
    userUrl = 'https://www.nytimes.com/2018/06/10/world/canada/g-7-justin-trudeau-trump.html'
    response = requests.get(userUrl)

    responseText = response.text.encode('UTF-8')
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    s = soup.find_all('p')

    string1 = str(s)
    
    arrayS = string1.split(' ')

    arrayS = [word.replace('<p', '').replace('</p>', '').replace('<code>', '').replace('</code>', '')
        .replace('class=', '').replace('href=', '').replace('>', '').replace('<p', '')
        .replace('\"', '').replace('\"', '').replace(',','') for word in arrayS]

    arrayS = list(filter(None, arrayS))

    article1 = scoredUrl('https://www.foxnews.com/media/trudeau-johnson-macron-appear-to-be-mocking-trump-at-nato-summit-in-surfaced-video', 6.5)
    article2 = scoredUrl('https://www.nbcnews.com/politics/donald-trump/trump-calls-trudeau-two-faced-after-hot-mic-catches-nato-n1095351', 8.0)
    article3 = scoredUrl('https://www.dailymail.co.uk/news/article-7753821/Justin-Trudeau-Emmanuel-Macron-Boris-Johnson-caught-appearing-gossip-Trump.html', 5.0)
    article4 = scoredUrl('https://www.theguardian.com/us-news/2019/dec/04/trump-describes-trudeau-as-two-faced-over-nato-hot-mic-video', 7.0)
    article5 = scoredUrl('https://abcnews.go.com/Politics/trudeau-washington-move-past-feud-trump-lobby-usmca/story?id=63820427', 6.0)
    article6 = scoredUrl('https://www.usatoday.com/story/news/politics/2018/11/01/trade-wars-canada-not-ready-forgive-trumps-insulting/1648045002/', 8.5)
    article7 = scoredUrl('https://www.scmp.com/news/world/article/2150067/trump-tweets-he-instructed-us-representatives-not-endorse-g7-joint', 2.4)
    article8 = scoredUrl('https://thehill.com/homenews/administration/472972-trump-caught-on-hot-mic-criticizing-media-talking-about-two-faced', 9.0)

    articleList = [article1, article2, article3, article4, article5, article6, article7, article8]
    #print(len(articleList))
    numeach = len(articleList)/numcpus
    #print("Num each", numeach)

    start = starttime()
    mpi()
    end = endtime()

    print(end - start)

