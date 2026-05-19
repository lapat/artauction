# 🎨 Art Auction Price Analyzer

A comprehensive web application that analyzes art auction prices and provides bidding recommendations based on historical data, market trends, and artwork characteristics.

## 🚀 Features

- **Historical Price Analysis**: Analyzes past 5 years of auction data for comparable works
- **Market Trend Prediction**: Uses statistical models to predict 10-year value projections
- **Quality Assessment**: Factors in provenance, condition, signature, and exhibition history
- **Bidding Strategy**: Provides conservative, target, and maximum bid recommendations
- **Auction House Premiums**: Considers major auction house and seasonal factors
- **ROI Calculations**: Projects return on investment over 10-year period

## 🎯 How It Works

1. **Input Artwork Details**: Artist, media type, dimensions, and auction information
2. **Quality Factors**: Rate provenance, condition, and value-adding attributes
3. **Market Analysis**: Compares to similar works and analyzes trends
4. **Price Recommendation**: Get detailed bidding strategy and value projections

## 🛠️ Quick Start

### Option 1: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open browser to http://localhost:5000
```

### Option 2: Deploy to Cloud

**Heroku Deployment** (Recommended - Free tier available):
```bash
# Install Heroku CLI, then:
heroku create your-art-analyzer-app
git push heroku main
```

**Vercel Deployment**:
```bash
# Install Vercel CLI, then:
vercel --prod
```

## 📊 Sample Data Included

The app comes pre-loaded with auction records for:
- **Pablo Picasso** (3 records) - Oil on canvas works
- **Claude Monet** (2 records) - Oil on canvas works  
- **Vincent van Gogh** (1 record) - Oil on canvas work
- **Andy Warhol** (2 records) - Screenprint works

## 🧪 Testing

Visit `/test` to run comprehensive tests:
- Sample artwork analysis tests
- Database connectivity tests  
- API endpoint tests

## 💡 Usage Tips

1. **Start with Sample Artists**: Click the sample artist buttons to see how the analyzer works
2. **Add Quality Factors**: Higher provenance and condition ratings significantly impact valuations
3. **Consider Auction Timing**: Spring and fall auctions typically command higher prices
4. **Use Multiple Scenarios**: Test different quality ratings to see price sensitivity

## 🔧 Technical Details

- **Backend**: Python Flask with SQLite database
- **Frontend**: Responsive HTML/CSS/JavaScript interface
- **Analysis Engine**: Statistical trend analysis with quality multipliers
- **Database**: SQLite with auction records table

## 💰 Deployment Costs

### Free Options:
- **Heroku Free Tier**: $0/month (limited hours)
- **Railway**: $0/month for small apps
- **PythonAnywhere**: $0/month (limited)

### Paid Options:
- **Heroku Hobby**: $7/month
- **DigitalOcean App Platform**: $5/month
- **Railway Pro**: $5/month
- **AWS Lightsail**: $3.50/month

### Domain (Optional):
- **Custom Domain**: $10-15/year via Namecheap/GoDaddy

**Recommended**: Start with Heroku free tier, upgrade to Hobby ($7/month) if needed.

## 🚀 Production Deployment

1. **Choose a hosting platform** (Heroku recommended)
2. **Set up database** (PostgreSQL for production)
3. **Configure environment variables**
4. **Set up custom domain** (optional)
5. **Enable HTTPS** (automatic with most platforms)

## 📈 Adding Your Own Data

Use the web interface or API to add auction records:

```javascript
// Add record via API
fetch('/add_record', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        artist: "Artist Name",
        title: "Artwork Title", 
        media: "Oil on canvas",
        width: 24,
        height: 30,
        date: "2024-01-15",
        hammer_price: 500000,
        estimate_low: 400000,
        estimate_high: 600000,
        auction_house: "Christie's",
        provenance_quality: 4,
        condition_rating: 5,
        signature: true,
        dated_work: true,
        exhibition_history: true,
        literature: false
    })
});
```

## 🔒 Security Notes

- No sensitive data is stored
- All calculations are done server-side
- SQLite database is local to the application
- No user authentication required for basic functionality

## 📞 Support

For questions or issues:
1. Check the `/test` page for diagnostics
2. Review the browser console for JavaScript errors
3. Check server logs for backend issues

---

**Built for art collectors and dealers to make informed bidding decisions based on comprehensive market analysis.**