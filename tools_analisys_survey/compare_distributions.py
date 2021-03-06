import recreate_authors
import answers_project
import sys

files_dir = sys.argv[1]

authorList = recreate_authors.recreate(files_dir+"output_authors_ids_nobots.csv")
authorDict = answers_project.survey(files_dir+"answers_project.csv")

def activity(filename):
    input = open(filename, "r")

    activityDict = {}
    lineNumber = 1
    while 1:
        line = input.readline()
        if not line:
            break
        activityList = line[:-2].split(',')
        activityDict[authorList[lineNumber-1]] = activityList
        lineNumber +=1
    return activityDict

def list2r(name, inputList):
    returnString = name + " <- c("
    for dev in inputList:
        returnString += str(dev) + ", "
    returnString = returnString[:-2]
    returnString += ")"            
    return returnString


if __name__ == "__main__":
    activityDict = activity(files_dir+"output_commits_nobots.csv")

    allList = []
    surveyList = []
    for author_id in activityDict:
        sum_author = 0
        for month in range(-6,0):
            sum_author += int(activityDict[author_id][month])
        if sum_author:
            allList.append(sum_author)
            if author_id in authorDict:
                surveyList.append(sum_author)


    print list2r("all", allList)
    print list2r("survey", surveyList)
    print 'names(all) <- "all"'
    print 'names(survey) <- "survey"'
    print "summary(all)"
    print "summary(survey)"
    print "wilcox.test(survey,all)"
    print 'png("distribution_boxplot.png")'
    print 'boxplot(survey, all, log="y", main="Distribution of commits",  xlab="Population", ylab="Commits last 6 months (log)", names=c("surveyed active", "all active"))'
    print 'dev.off()'
