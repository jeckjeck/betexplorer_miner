library(jsonlite)
library(httr)
library(RCurl)
library(RMongo)
library(rjson)

hostname = ""
username = ""
password = ""

mongo <- mongoDbConnect("nba_standings", host=hostname)
authenticated <- dbAuthenticate(mongo, username, password)
output = RMongo::dbGetQuery(mongo,"dat","{}")

real = lapply(output[,1], fromJSON)

df <- data.frame(team=as.character(), wins=as.numeric(), losses=as.numeric(), stringsAsFactors = FALSE)


for (i in 1:length(real)){
  df[i,1] <- real[[i]]$team
  df[i,2] <- real[[i]]$wins
  df[i,3] <- real[[i]]$losses
}

df
