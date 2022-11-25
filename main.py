from website import create_app, db
from config import Config
from website.models import User, Post


app = create_app(Config=Config)

# shell context
@app.shell_context_processor
def make_context_processor():
    return {"db":db, "User":User, "Post":Post}

if __name__ == "__main__":
    app.run(debug=True)