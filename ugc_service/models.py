from datetime import datetime, UTC
from ugc_service.extensions import db


class Review(db.Model):
    """
    Отзыв пользователя к товару.
    Хранится в отдельном Flask-сервисе UGC.
    """

    __tablename__ = 'reviews'
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_HIDDEN = 'hidden'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_name': self.user_name,
            'text': self.text,
            'rating': self.rating,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }