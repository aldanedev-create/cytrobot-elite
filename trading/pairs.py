from database.models import TradingPair

class PairManager:
    def __init__(self, db, TradingPair):
        self.db = db
        self.TradingPair = TradingPair
    
    def get_active_pairs(self):
        return self.TradingPair.query.filter_by(is_active=True).all()
    
    def add_pair(self, pair_name, admin_id):
        existing = self.TradingPair.query.filter_by(pair_name=pair_name).first()
        if existing:
            return False, "Pair already exists"
        
        new_pair = self.TradingPair(pair_name=pair_name)
        self.db.session.add(new_pair)
        self.db.session.commit()
        
        return True, new_pair
    
    def toggle_pair(self, pair_id):
        pair = self.TradingPair.query.get(pair_id)
        if pair:
            pair.is_active = not pair.is_active
            self.db.session.commit()
            return True, pair
        return False, "Pair not found"