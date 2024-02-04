from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

from src import bcrypt, db
from src.accounts.models import User
from src.core.models import Comment, News

from .forms import LoginForm, RegisterForm,RecoveryForm,ChangePasswordForm
import logging
from datetime import datetime



accounts_bp = Blueprint("accounts", __name__)
logging.basicConfig(filename='monitoring.log', level=logging.INFO)
@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("core.home"))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        birth_date = form.birth_date.data
        if birth_date:
            user.birth_date = birth_date
        nickname = form.nickname.data
        if nickname:
            user.nickname = nickname

        if form.email.data == "adminToUkraine@hotmail.com" and form.password.data == "adminToUkraine":
            user.is_admin = True
        
        
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("You registered and are now logged in. Welcome!", "success")
        return redirect(url_for("core.home"))
    return render_template("accounts/register.html", form=form)


@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("core.home"))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("core.home"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("accounts/login.html", form=form)
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/logout")
@login_required
def logout():
    logging.info(
    f"Time: {datetime.now()}, "
    f"IP: {request.remote_addr}, "
    f"User-Agent: {request.user_agent}, "
    f"Endpoint: {request.endpoint}, "
    f"Method: {request.method}, "
    f"Referer: {request.headers.get('Referer', 'None')}, "
    f"Language: {request.headers.get('Accept-Language', 'None')}"
)

    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("accounts.login"))


@accounts_bp.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):

    # Check if the user is trying to access another user's profile
    if current_user.id != user_id:
        logging.info(
            f"Time: A4: Insecure direct object references occured. {datetime.now()}, "
        )
    logging.info(
        f"Time: {datetime.now()}, "
        f"User ID: {current_user.get_id()}, "
        f"URL: {request.url}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    user = User.query.get(user_id)
    if not user:
        return render_template("401.html", message="User not found")
    
    userMail = user.email
    userNickname = user.nickname
    userBirthDate = user.birth_date
    commentAll = Comment.query.filter_by(user_id=user_id).all() 
    commentNewsIds = [comment.news_id for comment in commentAll]

    return render_template("accounts/userProfile.html", user=user, userMail=userMail, userNickname=userNickname, userBirthDate=userBirthDate, commentAll=commentAll, commentNewsIds=commentNewsIds)

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from src import app, s,mail

from src import limiter


@accounts_bp.route('/recover', methods=['GET', 'POST'])
@limiter.limit("3 per day")
def recover():
    logging.info(
        f"Time: {datetime.now()}, "
        f"IP: {request.remote_addr}, "
        f"User-Agent: {request.user_agent}, "
        f"Endpoint: {request.endpoint}, "
        f"Method: {request.method}, "
        f"Referer: {request.headers.get('Referer', 'None')}, "
        f"Language: {request.headers.get('Accept-Language', 'None')}"
    )
    form = RecoveryForm(request.form)
    if request.method == 'POST' and form.validate():
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        # Check if the user is trying to recover an account that does not exist
        # Or if the user is trying to recover an account that is not theirs 
        if user:

            token = s.dumps(email, salt='email-recover')
            msg = Message('Password Reset Request', sender='your-email@example.com', recipients=[email])

            link = url_for('accounts.reset_token', token=token, _external=True)
            msg.body = 'Your link to reset your password is {}'.format(link)

            mail.send(msg)

            flash('A password reset link has been sent to your email.', 'info')
            return redirect(url_for('accounts.login'))
        else:
            flash('The email is not registered.', 'danger')
            return redirect(url_for('accounts.recover'))

    return render_template('accounts/recovery.html', form=form)


@accounts_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_token(token):
    logging.info(
    f"Time: {datetime.now()}, "
    f"IP: {request.remote_addr}, "
    f"User-Agent: {request.user_agent}, "
    f"Endpoint: {request.endpoint}, "
    f"Method: {request.method}, "
    f"Referer: {request.headers.get('Referer', 'None')}, "
    f"Language: {request.headers.get('Accept-Language', 'None')}"
    )

    form = ChangePasswordForm(request.form)
    try:
        email = s.loads(token, salt='email-recover', max_age=3600)
    except SignatureExpired:
        
        flash('The password reset link is expired.', 'danger')
        return redirect(url_for('accounts.recover'))

    
    if request.method == 'POST'and form.validate():
        new_password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('accounts.login'))

    return render_template('accounts/reset_password.html', token=token, form=form, email=email )