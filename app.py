from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

app = Flask(__name__)

@dataclass
class AuctionRecord:
    artist: str
    title: str
    media: str
    width: float
    height: float
    date: str
    hammer_price: float
    estimate_low: float
    estimate_high: float
    auction_house: str
    provenance_quality: int
    condition_rating: int
    signature: bool
    dated_work: bool
    exhibition_history: bool
    literature: bool

class AuctionDatabase:
    def __init__(self, db_path: str = "auction_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                title TEXT,
                media TEXT,
                width REAL,
                height REAL,
                date TEXT,
                hammer_price REAL,
                estimate_low REAL,
                estimate_high REAL,
                auction_house TEXT,
                provenance_quality INTEGER,
                condition_rating INTEGER,
                signature BOOLEAN,
                dated_work BOOLEAN,
                exhibition_history BOOLEAN,
                literature BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_record(self, record: AuctionRecord):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auctions (
                artist, title, media, width, height, date, hammer_price,
                estimate_low, estimate_high, auction_house, provenance_quality,
                condition_rating, signature, dated_work, exhibition_history, literature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.artist, record.title, record.media, record.width, record.height,
            record.date, record.hammer_price, record.estimate_low, record.estimate_high,
            record.auction_house, record.provenance_quality, record.condition_rating,
            record.signature, record.dated_work, record.exhibition_history, record.literature
        ))
        
        conn.commit()
        conn.close()
    
    def get_artist_records(self, artist: str, years_back: int = 5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=years_back*365)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM auctions 
            WHERE artist LIKE ? AND date >= ?
            ORDER BY date DESC
        ''', (f'%{artist}%', cutoff_date))
        
        records = []
        for row in cursor.fetchall():
            records.append(AuctionRecord(
                artist=row[1], title=row[2], media=row[3], width=row[4], height=row[5],
                date=row[6], hammer_price=row[7], estimate_low=row[8], estimate_high=row[9],
                auction_house=row[10], provenance_quality=row[11], condition_rating=row[12],
                signature=bool(row[13]), dated_work=bool(row[14]), 
                exhibition_history=bool(row[15]), literature=bool(row[16])
            ))
        
        conn.close()
        return records

class PriceAnalyzer:
    def __init__(self, database: AuctionDatabase):
        self.db = database
        # Market averages by media type (price per square inch)
        self.media_averages = {
            'oil on canvas': {'min': 50, 'avg': 500, 'max': 5000, 'premium_multiplier': 1.5},
            'acrylic on canvas': {'min': 30, 'avg': 250, 'max': 2500, 'premium_multiplier': 1.2},
            'watercolor': {'min': 20, 'avg': 150, 'max': 1500, 'premium_multiplier': 1.0},
            'screenprint': {'min': 10, 'avg': 100, 'max': 1000, 'premium_multiplier': 0.8},
            'lithograph': {'min': 15, 'avg': 120, 'max': 1200, 'premium_multiplier': 0.9},
            'sculpture': {'min': 100, 'avg': 1000, 'max': 10000, 'premium_multiplier': 2.0},
            'mixed media': {'min': 40, 'avg': 300, 'max': 3000, 'premium_multiplier': 1.1},
            'charcoal': {'min': 25, 'avg': 180, 'max': 1800, 'premium_multiplier': 0.9},
            'pastel': {'min': 30, 'avg': 200, 'max': 2000, 'premium_multiplier': 1.0}
        }
        
        # Artist tier estimates (rough market positioning)
        self.artist_tiers = {
            'tier_1': {'multiplier': 50, 'examples': ['Picasso', 'Van Gogh', 'Monet', 'Da Vinci', 'Warhol']},
            'tier_2': {'multiplier': 15, 'examples': ['Pollock', 'Rothko', 'Basquiat', 'Hockney']},
            'tier_3': {'multiplier': 5, 'examples': ['Contemporary masters', 'Regional famous']},
            'tier_4': {'multiplier': 2, 'examples': ['Emerging artists', 'Local artists']},
            'unknown': {'multiplier': 1, 'examples': ['Unknown or new artists']}
        }
    
    def calculate_size_area(self, width: float, height: float) -> float:
        return width * height
    
    def get_comparable_works(self, artist: str, media: str, target_width: float, 
                          target_height: float, tolerance: float = 0.3):
        all_records = self.db.get_artist_records(artist)
        target_area = self.calculate_size_area(target_width, target_height)
        
        comparables = []
        for record in all_records:
            if record.media.lower() == media.lower():
                record_area = self.calculate_size_area(record.width, record.height)
                size_ratio = min(record_area, target_area) / max(record_area, target_area)
                
                if size_ratio >= (1 - tolerance):
                    comparables.append(record)
        
        return comparables
    
    def calculate_price_per_square_inch(self, record: AuctionRecord) -> float:
        area = self.calculate_size_area(record.width, record.height)
        if area <= 0:
            return 0
        return record.hammer_price / area
    
    def analyze_historical_trends(self, comparables):
        if not comparables:
            return {"error": "No comparable works found"}
        
        yearly_data = {}
        for record in comparables:
            year = record.date[:4]
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(record.hammer_price)
        
        yearly_averages = {}
        for year, prices in yearly_data.items():
            yearly_averages[year] = statistics.mean(prices)
        
        years = [int(y) for y in yearly_averages.keys()]
        prices = list(yearly_averages.values())
        
        if len(years) > 1:
            n = len(years)
            sum_xy = sum(x * y for x, y in zip(years, prices))
            sum_x = sum(years)
            sum_y = sum(prices)
            sum_x2 = sum(x * x for x in years)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            trend_direction = "increasing" if slope > 0 else "decreasing"
            trend_strength = abs(slope) / statistics.mean(prices) * 100
        else:
            slope = 0
            trend_direction = "stable"
            trend_strength = 0
        
        return {
            "yearly_data": yearly_averages,
            "trend_slope": slope,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "total_records": len(comparables)
        }
    
    def calculate_quality_multiplier(self, provenance: int, condition: int, 
                                   signature: bool, dated: bool, 
                                   exhibition: bool, literature: bool) -> float:
        base_multiplier = 1.0
        
        provenance_multipliers = [0.7, 0.8, 1.0, 1.3, 1.6]
        base_multiplier *= provenance_multipliers[provenance - 1]
        
        condition_multipliers = [0.5, 0.7, 1.0, 1.2, 1.4]
        base_multiplier *= condition_multipliers[condition - 1]
        
        if signature:
            base_multiplier *= 1.15
        if dated:
            base_multiplier *= 1.1
        if exhibition:
            base_multiplier *= 1.2
        if literature:
            base_multiplier *= 1.25
        
        return base_multiplier
    
    def predict_future_value(self, current_estimate: float, trend_slope: float, 
                           years_forward: int = 10) -> float:
        predicted_value = current_estimate + (trend_slope * years_forward)
        maturity_factor = 1 + (0.02 * years_forward)
        predicted_value *= maturity_factor
        
        return max(predicted_value, current_estimate * 0.5)
    
    def analyze_auction_factors(self, auction_house: str, season: str):
        major_houses = ["christie's", "sotheby's", "phillips", "bonhams"]
        house_multiplier = 1.15 if auction_house.lower() in major_houses else 1.0
        
        seasonal_multipliers = {
            "spring": 1.05,
            "fall": 1.1,
            "winter": 0.95,
            "summer": 0.9
        }
        
        season_multiplier = seasonal_multipliers.get(season.lower(), 1.0)
        
        return {
            "auction_house_premium": house_multiplier,
            "seasonal_multiplier": season_multiplier,
            "combined_factor": house_multiplier * season_multiplier
        }
    
    def get_season(self, date: datetime) -> str:
        month = date.month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"
    
    def estimate_artist_tier(self, artist: str) -> str:
        """Estimate artist tier based on name recognition"""
        artist_lower = artist.lower()
        
        # Check against known high-value artists
        tier_1_keywords = ['picasso', 'van gogh', 'monet', 'da vinci', 'leonardo', 'warhol', 
                          'renoir', 'cezanne', 'degas', 'manet', 'matisse', 'kandinsky']
        tier_2_keywords = ['pollock', 'rothko', 'basquiat', 'hockney', 'koons', 'banksy',
                          'hirst', 'kaws', 'kusama', 'richter']
        tier_3_keywords = ['contemporary', 'modern', 'abstract', 'impressionist']
        
        for keyword in tier_1_keywords:
            if keyword in artist_lower:
                return 'tier_1'
        
        for keyword in tier_2_keywords:
            if keyword in artist_lower:
                return 'tier_2'
                
        for keyword in tier_3_keywords:
            if keyword in artist_lower:
                return 'tier_3'
                
        # Default to tier_4 for unknown artists
        return 'tier_4'
    
    def generate_recommendation(self, artist: str, media: str, width: float, 
                              height: float, auction_house: str, auction_date: str,
                              provenance: int, condition: int, signature: bool,
                              dated: bool, exhibition: bool, literature: bool):
        
        # First try to find comparable works in database
        comparables = self.get_comparable_works(artist, media, width, height)
        
        if comparables:
            # Use existing database-driven analysis
            return self.analyze_with_comparables(comparables, artist, media, width, height,
                                               auction_house, auction_date, provenance, 
                                               condition, signature, dated, exhibition, literature)
        
        # Fallback: Generate estimate using market averages
        return self.generate_market_estimate(artist, media, width, height, auction_house, 
                                          auction_date, provenance, condition, signature, 
                                          dated, exhibition, literature)
    
    def analyze_with_comparables(self, comparables, artist: str, media: str, width: float, 
                              height: float, auction_house: str, auction_date: str,
                              provenance: int, condition: int, signature: bool,
                              dated: bool, exhibition: bool, literature: bool):
        
        trend_analysis = self.analyze_historical_trends(comparables)
        
        prices_per_sqin = [self.calculate_price_per_square_inch(record) 
                          for record in comparables]
        avg_price_per_sqin = statistics.mean(prices_per_sqin)
        median_price_per_sqin = statistics.median(prices_per_sqin)
        
        target_area = self.calculate_size_area(width, height)
        base_estimate = median_price_per_sqin * target_area
        
        quality_multiplier = self.calculate_quality_multiplier(
            provenance, condition, signature, dated, exhibition, literature
        )
        
        adjusted_estimate = base_estimate * quality_multiplier
        
        auction_date_obj = datetime.strptime(auction_date, '%Y-%m-%d')
        season = self.get_season(auction_date_obj)
        auction_factors = self.analyze_auction_factors(auction_house, season)
        
        final_estimate = adjusted_estimate * auction_factors['combined_factor']
        
        conservative_bid = final_estimate * 0.7
        target_bid = final_estimate * 0.85
        max_bid = final_estimate * 1.1
        
        future_value = self.predict_future_value(
            final_estimate, trend_analysis['trend_slope']
        )
        
        roi_10_year = ((future_value - target_bid) / target_bid) * 100 if target_bid > 0 else 0
        
        return {
            "artist": artist,
            "media": media,
            "dimensions": f"{width}\" x {height}\" ({target_area:.1f} sq in)",
            "comparable_sales": len(comparables),
            "base_estimate": round(base_estimate, 2),
            "quality_adjusted": round(adjusted_estimate, 2),
            "final_estimate": round(final_estimate, 2),
            "bidding_strategy": {
                "conservative_bid": round(conservative_bid, 2),
                "target_bid": round(target_bid, 2),
                "maximum_bid": round(max_bid, 2)
            },
            "market_analysis": {
                "trend_direction": trend_analysis['trend_direction'],
                "trend_strength": f"{trend_analysis['trend_strength']:.1f}% per year",
                "price_per_sq_inch": f"${avg_price_per_sqin:.2f} avg, ${median_price_per_sqin:.2f} median",
                "data_source": "Historical auction records"
            },
            "future_projection": {
                "estimated_value_10_years": round(future_value, 2),
                "projected_roi": f"{roi_10_year:.1f}%"
            },
            "auction_factors": auction_factors
        }
    
    def generate_market_estimate(self, artist: str, media: str, width: float, 
                               height: float, auction_house: str, auction_date: str,
                               provenance: int, condition: int, signature: bool,
                               dated: bool, exhibition: bool, literature: bool):
        """Generate estimate using market averages when no comparable data exists"""
        
        media_key = media.lower()
        target_area = self.calculate_size_area(width, height)
        
        # Get media baseline
        if media_key in self.media_averages:
            media_data = self.media_averages[media_key]
        else:
            # Default to oil on canvas if media not found
            media_data = self.media_averages['oil on canvas']
        
        # Estimate artist tier and get multiplier
        artist_tier = self.estimate_artist_tier(artist)
        artist_multiplier = self.artist_tiers[artist_tier]['multiplier']
        
        # Calculate base price per square inch
        base_price_per_sqin = media_data['avg'] * artist_multiplier
        
        # Apply size factor (larger works often command premium per sq in)
        if target_area > 1000:  # Large works
            size_multiplier = 1.3
        elif target_area > 500:  # Medium works 
            size_multiplier = 1.1
        else:  # Small works
            size_multiplier = 0.9
            
        base_price_per_sqin *= size_multiplier
        base_estimate = base_price_per_sqin * target_area
        
        # Apply quality multiplier
        quality_multiplier = self.calculate_quality_multiplier(
            provenance, condition, signature, dated, exhibition, literature
        )
        
        adjusted_estimate = base_estimate * quality_multiplier
        
        # Apply auction factors
        auction_date_obj = datetime.strptime(auction_date, '%Y-%m-%d')
        season = self.get_season(auction_date_obj)
        auction_factors = self.analyze_auction_factors(auction_house, season)
        
        final_estimate = adjusted_estimate * auction_factors['combined_factor']
        
        # Calculate bidding strategy
        conservative_bid = final_estimate * 0.7
        target_bid = final_estimate * 0.85
        max_bid = final_estimate * 1.1
        
        # Future value prediction (conservative 3% annual growth)
        future_value = final_estimate * (1.03 ** 10)
        roi_10_year = ((future_value - target_bid) / target_bid) * 100 if target_bid > 0 else 0
        
        # Create market trend simulation
        trend_direction = "stable" if artist_tier in ['tier_3', 'tier_4'] else "increasing"
        trend_strength = 2.0 if artist_tier == 'tier_1' else 1.5 if artist_tier == 'tier_2' else 1.0
        
        return {
            "artist": artist,
            "media": media,
            "dimensions": f"{width}\" x {height}\" ({target_area:.1f} sq in)",
            "comparable_sales": 0,
            "base_estimate": round(base_estimate, 2),
            "quality_adjusted": round(adjusted_estimate, 2),
            "final_estimate": round(final_estimate, 2),
            "bidding_strategy": {
                "conservative_bid": round(conservative_bid, 2),
                "target_bid": round(target_bid, 2),
                "maximum_bid": round(max_bid, 2)
            },
            "market_analysis": {
                "trend_direction": trend_direction,
                "trend_strength": f"{trend_strength:.1f}% per year",
                "price_per_sq_inch": f"${base_price_per_sqin:.2f} estimated",
                "artist_tier": artist_tier.replace('_', ' ').title(),
                "data_source": "Market averages (no historical data available)"
            },
            "future_projection": {
                "estimated_value_10_years": round(future_value, 2),
                "projected_roi": f"{roi_10_year:.1f}%"
            },
            "auction_factors": auction_factors,
            "estimation_note": f"Estimate based on market averages for {media_data} and {artist_tier.replace('_', ' ')} artist positioning"
        }

# Initialize database and analyzer
database = AuctionDatabase()
analyzer = PriceAnalyzer(database)

# Load sample data
def load_sample_data():
    sample_data = [
        AuctionRecord("Pablo Picasso", "Woman with Hat", "Oil on canvas", 24, 36, "2023-05-15", 
                     850000, 600000, 800000, "Christie's", 5, 4, True, True, True, True),
        AuctionRecord("Pablo Picasso", "Blue Period Portrait", "Oil on canvas", 20, 30, "2022-11-10", 
                     720000, 500000, 700000, "Sotheby's", 4, 5, True, False, True, True),
        AuctionRecord("Pablo Picasso", "Cubist Composition", "Oil on canvas", 28, 32, "2021-05-20", 
                     950000, 800000, 1000000, "Phillips", 5, 4, True, True, False, True),
        AuctionRecord("Claude Monet", "Water Lilies Study", "Oil on canvas", 25, 30, "2023-11-15", 
                     2100000, 1800000, 2000000, "Christie's", 5, 5, True, True, True, True),
        AuctionRecord("Claude Monet", "Poplar Trees", "Oil on canvas", 24, 28, "2022-05-12", 
                     1850000, 1500000, 1800000, "Sotheby's", 4, 4, True, False, True, True),
        AuctionRecord("Vincent van Gogh", "Landscape Study", "Oil on canvas", 20, 24, "2023-03-08", 
                     5200000, 4000000, 5000000, "Christie's", 5, 3, True, True, True, True),
        AuctionRecord("Andy Warhol", "Campbell's Soup", "Screenprint", 32, 32, "2023-09-20", 
                     185000, 150000, 200000, "Phillips", 3, 5, True, True, False, False),
        AuctionRecord("Andy Warhol", "Marilyn Portrait", "Screenprint", 36, 36, "2022-10-15", 
                     220000, 180000, 220000, "Sotheby's", 4, 4, True, True, True, False),
    ]
    
    existing = database.get_artist_records("Pablo Picasso")
    if not existing:
        for record in sample_data:
            database.add_record(record)

load_sample_data()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        
        result = analyzer.generate_recommendation(
            artist=data['artist'],
            media=data['media'],
            width=float(data['width']),
            height=float(data['height']),
            auction_house=data['auction_house'],
            auction_date=data['auction_date'],
            provenance=int(data.get('provenance', 3)),
            condition=int(data.get('condition', 4)),
            signature=data.get('signature', True),
            dated=data.get('dated', False),
            exhibition=data.get('exhibition', False),
            literature=data.get('literature', False)
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        data = request.json
        
        record = AuctionRecord(
            artist=data['artist'],
            title=data['title'],
            media=data['media'],
            width=float(data['width']),
            height=float(data['height']),
            date=data['date'],
            hammer_price=float(data['hammer_price']),
            estimate_low=float(data['estimate_low']),
            estimate_high=float(data['estimate_high']),
            auction_house=data['auction_house'],
            provenance_quality=int(data['provenance_quality']),
            condition_rating=int(data['condition_rating']),
            signature=data['signature'],
            dated_work=data['dated_work'],
            exhibition_history=data['exhibition_history'],
            literature=data['literature']
        )
        
        database.add_record(record)
        return jsonify({"success": True, "message": "Record added successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)