from datetime import datetime

from flask_login import UserMixin

from ..accounts.models import User

from src import bcrypt, db


class News(db.Model):
    __tablename__ = 'news'


    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=True)
    img_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    publishedAt = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(255), nullable=True)
    

    def __repr__(self):
        return f"<News {self.id}>"
    
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    news = db.relationship('News', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))


    def __repr__(self):
        return f"<Comment {self.id}>"
    



    
