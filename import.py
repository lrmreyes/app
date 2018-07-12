import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    # Opens the zips file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)
    next(reader, None)
    # Iterate over the rows of the opened CSV file.
    for row in reader:
        # Execute database queries, one per row.
        db.execute("INSERT INTO locations (zipcode, city, statecode, latitude, longitude, population) VALUES (:u, :v, :w, :x, :y, :z)",
        {"u": row[0], "v": row[1], "w": row[2], "x": row[3], "y": row[4], "z": row[5]})
    # Technically this is when all of the queries we've made happen!
    db.commit()

if __name__ == "__main__":
    main()