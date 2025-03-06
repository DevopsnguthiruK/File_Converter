from datetime import datetime
from app.models import db

class ConversionLog(db.Model):
    __tablename__ = 'conversion_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(5), db.ForeignKey('users.user_id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    converted_format = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('conversions', lazy=True))
    
    def __repr__(self):
        return f'<ConversionLog {self.id}: {self.original_filename}>'