from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:

    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = model(**data)
        return db_model

    def get_or_create_comment(self, session, model, data):
        db_model = session.query(model).filter(model.number == data['number']).first()
        if not db_model:
            db_model = model(**data)
        return db_model

    def create_post(self, data: dict):
        session = self.maker()
        tags = map(lambda tag_data: self.get_or_create(session,
                                                       models.Tag,
                                                       tag_data
                                                       ), data['tags'])
        comments = map(lambda comment_id: self.get_or_create_comment(session,
                                                                     models.Comments,
                                                                     comment_id
                                                                     ), data['comments'])
        author = self.get_or_create(session, models.Author, data['author'])
        post = self.get_or_create(session, models.Post, data['post_data'])
        post.author = author
        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)


        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()