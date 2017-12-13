library(jsonlite)
library(httr)
library(RCurl)
library(RMongo)
library(rjson)

hostname = ""
username = "username"
password = "password"

mongo <- mongoDbConnect("nba_standings", host= hostname)

authenticated <- dbAuthenticate(mongo, username, password)
output = RMongo::dbGetQuery(mongo,"dat","{}")

real = lapply(output[,1], fromJSON)

