# BlackJack Casino Simulator

A professional, feature-rich BlackJack simulator built with Python Flask and modern web technologies. Experience the thrill of casino BlackJack with realistic gameplay, beautiful animations, and authentic casino features.

![BlackJack Casino](https://img.shields.io/badge/BlackJack-Casino-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### Core Gameplay
- **Standard Casino Rules**: Follows authentic BlackJack rules
- **Multiple Actions**: Hit, Stand, Double Down, Split, Insurance
- **Realistic Payouts**: 3:2 for BlackJack, 2:1 for Insurance
- **Dealer AI**: Automatic dealer play following casino rules (hit on 16, stand on 17+)

### Visual Experience
- **Casino Table Design**: Authentic green felt table with wooden rails
- **Realistic Cards**: Beautiful card designs with smooth dealing animations
- **3D Casino Chips**: Professional chip design with hover effects
- **Smooth Animations**: Cards deal one at a time with realistic physics
- **Responsive Design**: Works perfectly on desktop and mobile

### Betting System
- **Chip-Based Betting**: Click chips to build your bet (additive system)
- **Undo/Clear**: Remove chips with undo or clear all
- **All-In Option**: Bet your entire balance with one click
- **Balance Management**: Add funds when balance runs low
- **Auto-Next Hand**: Seamless continuous gameplay

### Advanced Features
- **Split Hands**: Split pairs and play multiple hands simultaneously
- **Insurance**: Protect against dealer BlackJack
- **Statistics Tracking**: Track wins, losses, BlackJacks, and profit
- **Session Persistence**: Game state maintained across browser sessions

## Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 2.3.3**: Web framework for API and routing
- **Object-Oriented Design**: Clean, maintainable code structure
- **Session Management**: In-memory game state storage

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients, animations, and flexbox
- **JavaScript (ES6+)**: Interactive gameplay and API communication
- **Font Awesome**: Professional icons and symbols

### Key Technologies
- **CSS Animations**: Smooth card dealing and chip interactions
- **CSS Grid/Flexbox**: Responsive layout system
- **Fetch API**: Modern HTTP requests
- **JSON**: Data serialization and API responses
- **SVG**: Scalable favicon and graphics

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BlackJack-Simulator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### Alternative: Use the launcher
```bash
python run_game.py
```
Choose between command-line or web version.

## How to Play

### Basic Gameplay
1. **Place Your Bet**: Click casino chips to build your bet amount
2. **Deal Cards**: Click "Place Bet" to start the hand
3. **Make Decisions**: 
   - **Hit**: Take another card
   - **Stand**: Keep your current hand
   - **Double Down**: Double your bet and take exactly one more card
   - **Split**: Split pairs into two separate hands
   - **Insurance**: Protect against dealer BlackJack (when dealer shows Ace)

### Betting System
- **Additive Chips**: Click multiple chips to build your bet
- **Undo**: Remove the last chip you selected
- **Clear**: Remove all selected chips
- **All-In**: Bet your entire balance

### Winning Conditions
- **BlackJack**: 21 with first two cards (3:2 payout)
- **Win**: Beat dealer without going over 21
- **Push**: Tie with dealer (bet returned)
- **Lose**: Go over 21 or dealer beats you

## Project Structure

```
BlackJack-Simulator/
├── app.py                 # Flask web application
├── BlackJack Simulator.py # Command-line version
├── run_game.py           # Game launcher
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment configuration
├── README.md            # This file
├── static/
│   └── favicon.svg      # Website favicon
└── templates/
    └── index.html       # Web interface
```

## Configuration

### Game Settings
- **Starting Balance**: $1000
- **Deck Count**: 6 decks (casino standard)
- **Shuffle Point**: When less than 52 cards remain
- **BlackJack Payout**: 3:2
- **Insurance Payout**: 2:1

### Customization
Edit `app.py` to modify:
- Starting balance
- Number of decks
- Payout ratios
- Game rules

## Deployment

### Local Development
```bash
python app.py
```
Runs on `http://localhost:5000` with debug mode enabled.

### Production Deployment

#### Option 1: Heroku
1. The `Procfile` is already configured:
   ```
   web: gunicorn app:app
   ```

2. Dependencies are already in `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```

3. Deploy to Heroku:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

#### Option 2: PythonAnywhere
1. Upload files to PythonAnywhere
2. Create a new web app
3. Set the source code to your project directory
4. Configure WSGI file to point to `app.py`

#### Option 3: VPS/Cloud Server
1. Install Python and pip on your server
2. Clone the repository
3. Install dependencies: `pip install -r requirements.txt`
4. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

#### Option 4: Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t blackjack-casino .
docker run -p 5000:5000 blackjack-casino
```

## Customization

### Styling
- Modify CSS in `templates/index.html` to change colors, fonts, or layout
- Update chip colors and card designs
- Customize animations and transitions

### Game Rules
- Edit `app.py` to modify BlackJack rules
- Change payout ratios
- Adjust dealer behavior
- Add new game features

### Features
- Add sound effects
- Implement user accounts
- Add multiplayer support
- Create tournament modes

## Troubleshooting

### Common Issues

**Flask not found**
```bash
pip install Flask==2.3.3
```

**Port already in use**
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

**Cards not displaying**
- Check browser console for JavaScript errors
- Ensure all files are in correct directories
- Verify Flask static file serving

## Performance

- **Load Time**: < 2 seconds
- **Memory Usage**: < 50MB
- **Concurrent Users**: Supports multiple simultaneous players
- **Mobile Performance**: Optimized for mobile devices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Casino BlackJack rules and regulations
- Modern web design principles
- Flask documentation and community
- Font Awesome for icons

## Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the code comments for implementation details

---

**Enjoy your BlackJack experience!**