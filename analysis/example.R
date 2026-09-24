require("RPostgreSQL")

# Establish Connection
conn <- RPostgreSQL::dbConnect(
    dbDriver("PostgreSQL"),
    dbname=Sys.getenv("DATASTORE_DB"),
    host="postgres",
    port=5432,
    user=Sys.getenv("DATASTORE_USER"),
    password=Sys.getenv("DATASTORE_PASSWORD")
)

# Example Query
raw_bins <- dbGetQuery(conn, "SELECT * FROM raw_bins")
View(raw_bins)