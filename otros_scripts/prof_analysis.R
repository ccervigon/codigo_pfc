library(RMySQL)

calendar_commit_month_author <- function(year, month, author){
	M <- rep(0, 31)
	if (length(author) == 0) return(M)
	for (i in 1:length(author[,1])){
		if ((as.numeric(format(strptime(author[i,2], "%Y-%m-%d %H:%M:%S"),'%m')) == month) &
			(as.numeric(format(strptime(author[i,2], "%Y-%m-%d %H:%M:%S"),'%Y')) == year)){
			M[as.numeric(format(strptime(author[i,2], "%Y-%m-%d %H:%M:%S"),'%d'))] <- M[as.numeric(format(strptime(author[i,2], "%Y-%m-%d %H:%M:%S"),'%d'))] + 1
		}
	}
	return(M)
}

con <- dbConnect(MySQL(),
		user="tthebosss", password="1234",
		dbname="openstack_authors", host="localhost")


rs <- dbSendQuery(con, 'SELECT MIN(date) FROM scmlog')
dat_min <- as.numeric(format(strptime(fetch(rs, n=-1)[1,1], "%Y-%m-%d %H:%M:%S"),'%Y'))
dbClearResult(rs)

rs <- dbSendQuery(con, 'SELECT MAX(date) FROM scmlog')
dat_max <- as.numeric(format(strptime(fetch(rs, n=-1)[1,1], "%Y-%m-%d %H:%M:%S"),'%Y'))
dbClearResult(rs)

rs <- dbSendQuery(con, 'SELECT * FROM companies')
companies <- fetch(rs, n=-1)
dbClearResult(rs)

rs <- dbSendQuery(con, 'SELECT upeople_id, company_id FROM upeople_companies WHERE upeople_id = ANY (SELECT upeople_id FROM people_upeople)')
upeople_companies <- fetch(rs, n=-1)
dbClearResult(rs)

rs <- dbSendQuery(con, 'SELECT people_id FROM people_upeople WHERE upeople_id = ANY 
						(SELECT upeople_id FROM upeople_companies)')
people <- fetch(rs, n=-1)
dbClearResult(rs)
tot_people <- length(people[,1])

authors <- list()
for (people in 1:tot_people){
	query <- sprintf('SELECT author_id, date FROM scmlog WHERE author_id = %s ORDER BY date', people)
	rs <- dbSendQuery(con, query)
	authors[people] <- list(fetch(rs, n=-1))
}

work_authors <- list()
for (author in 1:tot_people){
	print(c('Author', author))
	M <- c()
	for (year in dat_min:dat_max){
		for (month in 1:12){
			aut <- calendar_commit_month_author(year, month, authors[author][[1]])
			work_days <- 0
			for (i in 1:length(aut)){
				if (aut[i] != 0){
					work_days <- work_days + 1
				}
			}
			M[length(M)+1] <- work_days
		}
	#print(c('Vector rellenado', M))
	work_authors[author] <- M
	}
}

save(work_authors, 'work_authors.RData')
print(work_authors)

"
print (people[,1])
print (colnames(people))

print(dim(upeople_companies)[1])
print(tot_people)
print(fetch(dbSendQuery(con, 'SELECT count(*) from people')))
"

dbClearResult(rs)
dbDisconnect(con)