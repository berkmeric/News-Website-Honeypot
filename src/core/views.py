from flask import Blueprint, render_template
from flask_login import login_required , current_user
import requests
from .models import News, Comment
from ..accounts.models import User
from flask import request, redirect,url_for
from src import db
import logging

from datetime import datetime

logging.basicConfig(filename='monitoring.log', level=logging.INFO)

core_bp = Blueprint("core", __name__)

@core_bp.route("/")
def home():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    api_key = '75d9a1b243d149408373c756948c8538'
    api_endpoint = 'https://newsapi.org/v2/top-headlines?country=ua&apiKey=' + api_key
    response = requests.get(api_endpoint)
    news_data = response.json()

    if current_user.is_authenticated:
        user_email = current_user.email
    else:
        user_email = "Please Login to Read Latest News"

    for article in news_data['articles']:
        if article['title'] is not None and article['description'] is not None and article['url'] is not None and article['urlToImage'] is not None and article['content'] is not None and article['publishedAt'] is not None and article['author'] is not None:
            news = News(
                title=article['title'],
                description=article['description'],
                url=article['url'],
                img_url=article['urlToImage'],
                content = article['content'],
                publishedAt = article['publishedAt'],
                author = article['author']
            )
            if News.query.filter_by(title=article['title']).first() is None:
                db.session.add(news)
    
    db.session.commit()
    news = News.query.all()
    newsLatest = News.query.order_by(News.id.desc()).limit(4).all()
    news_latest_3 = News.query.order_by(News.id.desc()).limit(3).all()
    news_latest_4_after_3 = News.query.order_by(News.id.desc()).offset(3).limit(4).all()
    

    return render_template('core/index.html', news_data=news_data, news=news, newsLatest=newsLatest, news_latest_3=news_latest_3, news_latest_4_after_3=news_latest_4_after_3, user_email=user_email)

@core_bp.route("/details/<int:news_id>",methods=['GET', 'POST'])
@login_required
def detail(news_id):
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    new = News.query.get(news_id)
    
    if current_user.is_authenticated:
        user_email = current_user.email

    newsAll = News.query.all()
    
    comments = Comment.query.all()
    newsLatest = News.query.order_by(News.id.desc()).limit(5).all()

    if request.method == 'POST':
        comment_content = request.form['message']
        comment = Comment(content=comment_content, news_id=news_id, user_id=current_user.id)  
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("core.detail", news_id=news_id))
    
    commentAll = Comment.query.filter_by(news_id=news_id).all()

    return render_template('core/detail.html',new=new, user_email=user_email, newsAll=newsAll, newsLatest=newsLatest ,commentAll=commentAll, comments=comments)



@core_bp.route("/delete-comment/<int:comment_id>", methods=['POST'])
@login_required
def deleteComment(comment_id):
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    comment = Comment.query.get(comment_id)
    
    news_id = request.form.get('news_id')
    
    if comment is not None:
        
        db.session.delete(comment)
        db.session.commit()
           
    return redirect(url_for('core.detail', news_id=news_id))
    

@core_bp.route("/delete-comment-profile/<int:comment_id>", methods=['POST'])
def deleteCommentProfile(comment_id):
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    comment = Comment.query.get(comment_id)
    
    
    if comment is not None:
        
        db.session.delete(comment)
        db.session.commit()
           
    return redirect(url_for('accounts.user_profile', user_id=current_user.id))


@core_bp.route("/delete-comment-admin/<int:comment_id>", methods=['POST'])
@login_required
def deleteCommentAdmin(comment_id):
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    comment = Comment.query.get(comment_id)
    if comment is not None and current_user.is_admin:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('core.admin_comment'))


@core_bp.route("/delete-user-admin/<int:user_id>", methods=['POST'])
@login_required
def deleteUserAdmin(user_id):
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    user = User.query.get(user_id)
    if user is not None:
        
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('core.admin'))


@core_bp.route('/admin/users')
@login_required
def admin():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    if not current_user.is_admin:
        return render_template('404.html')
      # Return a 403 Forbidden error if the current user is not an admin
    comments = Comment.query.all()
    users = User.query.all()
    
    return render_template('core/admin.html', comments=comments, users=users)


@core_bp.route('/admin/comments')
@login_required
def admin_comment():

    if not current_user.is_admin:
        logging.info(
            f"Time: A8: Failure to Restrict URL Access occured. {datetime.now()}, "
        )

    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    
    comments = Comment.query.all()
    users = User.query.all()
    
    return render_template('core/admin_comment.html', comments=comments, users=users)

@core_bp.route("/search", methods=["GET", "POST"])
def search():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    if request.method == "POST":
        keyword = request.form.get("keyword")
        news_results = News.query.filter(News.title.ilike(f"%{keyword}%")).all()
        return render_template("core/search.html", news_results=news_results, keyword=keyword)
    return render_template("core/search.html")



#http://127.0.0.1:5000/redirect?url=https://owasp.org/

@core_bp.route('/redirect')
def goto():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    target_url = request.args.get('url', '')
    if target_url:
        # Check if target_url exists in the news model's URLs
        # If it does, redirect to the target_url
        # If it doesn't, log the attempt and redirect to the home page
        news = News.query.filter_by(url=target_url).first()
        if news:
            return redirect(target_url, code=302)
        else:
            logging.info(
                f"A10: Unvalidated Redirects and Forwards occured. {datetime.now()}, "
            )
    
        
    return redirect(target_url, code=302)





