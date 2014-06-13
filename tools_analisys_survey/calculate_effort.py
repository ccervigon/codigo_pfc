import recreate_authors
import answers_project
import compare_distributions
import sys

files_dir = sys.argv[1]

authorList = recreate_authors.recreate(files_dir+"output_authors_ids_nobots.csv")
authorDict = answers_project.survey(files_dir+"answers_project.csv")
activityDict = compare_distributions.activity(files_dir+"output_commits_nobots.csv")

semesterList = [-48, -42, -36, -30, -24, -18, -12, -6]

effortList = []

for threshold in range(1,51):
    effortDict = {}
    for author_id in activityDict:
        effortDict[author_id] = []
#        print activityDict[author_id]
        for semester in semesterList:
            commits = 0
            for month in range(semester, semester+6):
                commits += int(activityDict[author_id][month])
#                print month, commits
            if commits >= threshold:
                effortDict[author_id].append(6)
            else:
                effortDict[author_id].append(6.0 * commits/threshold)
#        print effortDict[author_id]
#    print effortDict 
    effortList.append(effortDict)
#print effortList

count = 1
print "# threshold, total_effort, semester1, semester2, semester3, semester4, ..."
for effortDict in effortList:

    effort_total = 0
    for author in effortDict:
        for effort_semester in effortDict[author]:
            effort_total += effort_semester

    effortList = [0] * len(semesterList) 
    for author in effortDict:
        effortList = [x + y for x, y in zip(effortList, effortDict[author])]

    print count, int(round(effort_total)), 
    for sem_effort in effortList:
        print int(round(sem_effort)),
    print
    count+=1
