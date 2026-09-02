from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app import models
from datetime import datetime


def create_topic(db: Session, title: str, content: str, author_id: int):
    topic = models.Topic(
        title=title,
        content=content,
        author_id=author_id
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def get_topics(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Topic).order_by(desc(models.Topic.created_at)).offset(skip).limit(limit).all()


def get_topic(db: Session, topic_id: int):
    return db.query(models.Topic).filter(models.Topic.id == topic_id).first()


def update_topic(db: Session, topic_id: int, title: str, content: str):
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if topic:
        topic.title = title
        topic.content = content
        topic.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(topic)
    return topic


def delete_topic(db: Session, topic_id: int):
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if topic:
        db.delete(topic)
        db.commit()
        return True
    return False


def increment_topic_views(db: Session, topic_id: int):
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if topic:
        topic.views += 1
        db.commit()
    return topic


def create_post(db: Session, content: str, author_id: int, topic_id: int, parent_post_id: int = None):
    post = models.Post(
        content=content,
        author_id=author_id,
        topic_id=topic_id,
        parent_post_id=parent_post_id
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    # Обновляем время обновления темы
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if topic:
        topic.updated_at = datetime.utcnow()
        db.commit()

    return post


def get_posts_by_topic(db: Session, topic_id: int):
    return db.query(models.Post).filter(
        models.Post.topic_id == topic_id,
        models.Post.parent_post_id.is_(None)
    ).order_by(models.Post.created_at).all()


def get_replies_by_post(db: Session, post_id: int):
    return db.query(models.Post).filter(
        models.Post.parent_post_id == post_id
    ).order_by(models.Post.created_at).all()


def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
        return True
    return False


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, email: str, username: str, password_hash: str):
    user = models.User(
        email=email,
        username=username,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user