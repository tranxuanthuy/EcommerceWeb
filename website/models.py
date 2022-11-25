from website import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from website import login
from hashlib import md5
from sqlalchemy import or_

# load User data for flask login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# sub_ followers (n-n) relationship between User and User 
followers = db.Table("followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"))
)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(140))
    receive_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<Message %s>' % self.message

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), index=True, unique=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    join_date = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    # relationship with Post table (1-n)
    posts = db.relationship('Post', backref="author", lazy="dynamic")
    # relationship with User table (n-n) followers
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic"
    )
    # relationship with Comment table (1-n) 
    comments = db.relationship('Comment', backref='author', lazy="dynamic")

    # follow
    def follow(self, user):
        if not self.is_following(user=user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user=user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    # password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # get link avatar(gravatar)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d'\
            % (digest, size)
    # get followed post
    def followed_posts(self):
        followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).\
            filter(followers.c.follower_id == self.id)
        my_posts = self.posts.filter_by(status=0)
        posts = followed_posts.union(my_posts).order_by(Post.timestamp.desc())
        return posts
    # get my post
    def my_posts(self):
        posts = self.posts.filter(or_(Post.status==None, Post.status==0)).order_by(Post.timestamp.desc())
        return posts
    # selled
    def selled(self):
        posts = self.posts.filter_by(status=1).order_by(Post.timestamp.desc())
        return posts
    # to String
    def __repr__(self) -> str:
        return "<User %s>" % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    image_url = db.Column(db.String(140))
    category = db.Column(db.String(50), index=True)
    price = db.Column(db.Integer, index=True)
    detail = db.Column(db.String(500))
    # đã bán hay chưa bán
    status = db.Column(db.Integer, default=0)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    # relationship with User table n-1
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # relationship with comment table 1-n
    comments = db.relationship('Comment', backref='post', lazy="dynamic")
    # all posts for explore page
    @staticmethod
    def all_posts():
        posts = Post.query.order_by(Post.timestamp.desc())
        return posts

    def __repr__(self) -> str:
        return "<Post %s>" % self.title

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    # relationship with Post table n-1
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    # relationship with User table n-1
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return "<Comment %s>" % self.comment
    