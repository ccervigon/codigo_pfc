import recreate_authors
import answers_project
import compare_distributions
import sys

files_dir = sys.argv[1]

authorList = recreate_authors.recreate(files_dir+"output_authors_ids_nobots.csv")
authorDict = answers_project.survey(files_dir+"answers_project.csv")
activityDict = compare_distributions.activity(files_dir+"output_commits_nobots.csv")

thresholdList = []

for threshold in range(0, 50):
#    print threshold
    tp, fn, tn, fp = (0, 0, 0, 0)
    for author_id in activityDict:
        if author_id in authorDict:
            if authorDict[author_id][-1] == 0: # no commits!
                continue
            commitment = authorDict[author_id][0][0]
#            print author_id, commitment,
            activity = 0
            for month in range(-6,0):
                activity += int(activityDict[author_id][month])
#            print activity,

            if (int(activity) > threshold and commitment == 'f'):
                tp += 1
#                print 'tp',
            elif int(activity) <= threshold and commitment != 'f':
                tn += 1
#                print 'tn',
            elif commitment == 'f':
                fn += 1
#                print 'fn',
            else:
                fp += 1
#                print 'fp',
#            print
    thresholdList.append([tp, fn, tn, fp])

i = 0
print "# threshold, [tp, fn, tn, fp], precision, recall, fmeasure, accuracy, goodness"
for threshold in thresholdList:
    print i+1, threshold,
    tp = threshold[0]
    fn = threshold[1]
    tn = threshold[2]
    fp = threshold[3]
    precision = round(tp*1.0/(tp+threshold[-1]),3)
    recall = round(tp*1.0/(tp+fn),3)
    fmeasure = round(2 * precision * recall / (precision + recall),3)
    accuracy = round((tp+tn)*1.0/(tp+fn+tn+fp),3)
    goodness = 1-round(abs((tp + fp)- (tp + fn))*1.0/(tp + fn + fp),3)

    print precision, recall, fmeasure, accuracy, goodness
    i+=1

