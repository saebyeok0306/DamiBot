import db
import utils

if __name__ == "__main__":
    db.init_db(True)
    result = utils.most_similar_title("v o l d e n u i t")
    print(result)