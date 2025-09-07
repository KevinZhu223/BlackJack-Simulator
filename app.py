from flask import Flask, render_template, request, jsonify, session
import random
import json
from datetime import datetime
from typing import List, Optional

app = Flask(__name__, static_folder='static')
app.secret_key = 'blackjack_secret_key_2024'

# Simple in-memory storage for game states (in production, use a database)
game_states = {}

class Card:
    def __init__(self, value: str, suit: str):
        self.value = value
        self.suit = suit
        self.suit_symbols = {'♥': 'hearts', '♦': 'diamonds', '♠': 'spades', '♣': 'clubs'}
        self.suit_name = self.suit_symbols.get(suit, suit)
        
    def get_value(self, current_score: int = 0) -> int:
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 11 if current_score + 11 <= 21 else 1
        return int(self.value)
    
    def to_dict(self):
        return {
            'value': self.value,
            'suit': self.suit,
            'suit_name': self.suit_name,
            'display': f"{self.value}{self.suit}"
        }

class Deck:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.min_cards_before_shuffle = 52
        self.create_deck()
        
    def create_deck(self):
        suits = ['♥', '♠', '♣', '♦']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(value, suit) for _ in range(self.num_decks) 
                     for suit in suits for value in values]
        self.shuffle()
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal_card(self) -> Optional[Card]:
        if len(self.cards) < self.min_cards_before_shuffle:
            self.create_deck()
        if not self.cards:
            self.create_deck()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        
    def add_card(self, card: Card):
        self.cards.append(card)
        
    def get_score(self) -> int:
        score = 0
        aces = []
        
        for card in self.cards:
            if card.value == 'A':
                aces.append(card)
            else:
                score += card.get_value()
                
        for ace in aces:
            score += ace.get_value(score)
            
        return score
    
    def can_split(self) -> bool:
        if len(self.cards) != 2:
            return False
        # Check if both cards have the same value (including face cards)
        val1 = self.cards[0].get_value()
        val2 = self.cards[1].get_value()
        return val1 == val2
    
    def can_double(self) -> bool:
        return len(self.cards) == 2
    
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.get_score() == 21
    
    def to_dict(self):
        return {
            'cards': [card.to_dict() for card in self.cards],
            'score': self.get_score(),
            'can_split': self.can_split(),
            'can_double': self.can_double(),
            'is_blackjack': self.is_blackjack()
        }

class GameState:
    def __init__(self):
        self.deck = Deck()
        self.player_hands: List[Hand] = [Hand()]
        self.dealer_hand = Hand()
        self.balance = 1000
        self.bets: List[int] = []
        self.current_hand = 0
        self.game_phase = 'betting'  # betting, playing, dealer, finished
        self.insurance_bet = 0
        self.statistics = {
            'hands_played': 0,
            'hands_won': 0,
            'hands_lost': 0,
            'blackjacks': 0,
            'money_won': 0,
            'money_lost': 0
        }
    
    def place_bet(self, amount: int) -> bool:
        if amount <= self.balance and amount > 0:
            self.balance -= amount
            self.bets.append(amount)
            return True
        return False
    
    def win_bet(self, hand_index: int = 0, multiplier: float = 1):
        if hand_index < len(self.bets):
            winnings = int(self.bets[hand_index] * (1 + multiplier))
            self.balance += winnings
            self.statistics['hands_won'] += 1
            self.statistics['money_won'] += winnings - self.bets[hand_index]
    
    def lose_bet(self, hand_index: int = 0):
        if hand_index < len(self.bets):
            self.statistics['hands_lost'] += 1
            self.statistics['money_lost'] += self.bets[hand_index]
    
    def push_bet(self, hand_index: int = 0):
        if hand_index < len(self.bets):
            self.balance += self.bets[hand_index]
    
    def clear_hands(self):
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.bets = []
        self.current_hand = 0
        self.insurance_bet = 0
        self.statistics['hands_played'] += 1
    
    def play_dealer(self):
        while self.dealer_hand.get_score() < 17:
            self.dealer_hand.add_card(self.deck.deal_card())
        
        # Compare hands and settle bets
        dealer_score = self.dealer_hand.get_score()
        dealer_bust = dealer_score > 21
        
        for i, hand in enumerate(self.player_hands):
            player_score = hand.get_score()
            if player_score > 21:
                self.lose_bet(i)
            elif dealer_bust:
                self.win_bet(i)
            elif player_score > dealer_score:
                self.win_bet(i)
            elif player_score < dealer_score:
                self.lose_bet(i)
            else:
                self.push_bet(i)
        
        self.game_phase = 'finished'
    
    def to_dict(self):
        return {
            'player_hands': [hand.to_dict() for hand in self.player_hands],
            'dealer_hand': self.dealer_hand.to_dict(),
            'balance': self.balance,
            'bets': self.bets,
            'current_hand': self.current_hand,
            'game_phase': self.game_phase,
            'insurance_bet': self.insurance_bet,
            'statistics': self.statistics
        }

def get_game_state():
    # Use a simple session ID for now (in production, use proper user authentication)
    session_id = session.get('session_id', 'default')
    
    if session_id not in game_states:
        game = GameState()
        save_game_state(game)
        return game
    else:
        # Reconstruct GameState from dictionary
        game_dict = game_states[session_id]
        game = GameState()
        game.balance = game_dict['balance']
        game.bets = game_dict['bets']
        game.current_hand = game_dict['current_hand']
        game.game_phase = game_dict['game_phase']
        game.insurance_bet = game_dict['insurance_bet']
        game.statistics = game_dict['statistics']
        
        # Reconstruct hands
        game.player_hands = []
        for hand_dict in game_dict['player_hands']:
            hand = Hand()
            for card_dict in hand_dict['cards']:
                card = Card(card_dict['value'], card_dict['suit'])
                hand.cards.append(card)
            game.player_hands.append(hand)
        
        # Reconstruct dealer hand
        dealer_dict = game_dict['dealer_hand']
        game.dealer_hand = Hand()
        for card_dict in dealer_dict['cards']:
            card = Card(card_dict['value'], card_dict['suit'])
            game.dealer_hand.cards.append(card)
        
        # Reconstruct deck (create a new deck since we can't serialize the full deck state)
        game.deck = Deck()
        
        return game

def save_game_state(game):
    """Helper function to save game state to in-memory storage"""
    session_id = session.get('session_id', 'default')
    if 'session_id' not in session:
        session['session_id'] = session_id
    game_states[session_id] = game.to_dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game-state')
def get_state():
    game = get_game_state()
    return jsonify(game.to_dict())

@app.route('/api/place-bet', methods=['POST'])
def place_bet():
    game = get_game_state()
    data = request.get_json()
    bet_amount = data.get('bet', 0)
    
    if game.game_phase != 'betting':
        return jsonify({'success': False, 'message': 'Not in betting phase'})
    
    if game.place_bet(bet_amount):
        game.game_phase = 'playing'
        # Deal initial cards
        game.player_hands[0].add_card(game.deck.deal_card())
        game.dealer_hand.add_card(game.deck.deal_card())
        game.player_hands[0].add_card(game.deck.deal_card())
        game.dealer_hand.add_card(game.deck.deal_card())
        
        # Check for blackjack
        if game.player_hands[0].is_blackjack():
            game.game_phase = 'finished'
            if game.dealer_hand.is_blackjack():
                game.push_bet()
            else:
                game.win_bet(multiplier=1.5)
                game.statistics['blackjacks'] += 1
        
        save_game_state(game)
        return jsonify({'success': True, 'game_state': game.to_dict()})
    
    return jsonify({'success': False, 'message': 'Invalid bet amount'})

@app.route('/api/insurance', methods=['POST'])
def insurance():
    game = get_game_state()
    data = request.get_json()
    take_insurance = data.get('insurance', False)
    
    if game.game_phase != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    if take_insurance and len(game.dealer_hand.cards) > 0 and game.dealer_hand.cards[0].value == 'A':
        insurance_bet = game.bets[0] // 2
        if game.place_bet(insurance_bet):
            game.insurance_bet = insurance_bet
            if game.dealer_hand.is_blackjack():
                game.balance += insurance_bet * 3  # 2:1 payout
                save_game_state(game)
                return jsonify({'success': True, 'game_state': game.to_dict(), 'insurance_result': 'win'})
            else:
                save_game_state(game)
                return jsonify({'success': True, 'game_state': game.to_dict(), 'insurance_result': 'lose'})
    
    return jsonify({'success': True, 'game_state': game.to_dict()})

@app.route('/api/hit', methods=['POST'])
def hit():
    try:
        game = get_game_state()
        
        if game.game_phase != 'playing':
            return jsonify({'success': False, 'message': 'Not in playing phase'})
        
        current_hand = game.player_hands[game.current_hand]
        current_hand.add_card(game.deck.deal_card())
        
        if current_hand.get_score() > 21:
            game.lose_bet(game.current_hand)
            game.current_hand += 1
            
            if game.current_hand >= len(game.player_hands):
                game.game_phase = 'dealer'
                game.play_dealer()
            else:
                game.game_phase = 'playing'
        elif current_hand.get_score() == 21:
            game.current_hand += 1
            if game.current_hand >= len(game.player_hands):
                game.game_phase = 'dealer'
                game.play_dealer()
            else:
                game.game_phase = 'playing'
        
        save_game_state(game)
        return jsonify({'success': True, 'game_state': game.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/stand', methods=['POST'])
def stand():
    game = get_game_state()
    
    if game.game_phase != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    game.current_hand += 1
    if game.current_hand >= len(game.player_hands):
        game.game_phase = 'dealer'
        game.play_dealer()
    else:
        game.game_phase = 'playing'
    
    save_game_state(game)
    return jsonify({'success': True, 'game_state': game.to_dict()})

@app.route('/api/double', methods=['POST'])
def double_down():
    game = get_game_state()
    
    if game.game_phase != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    current_hand = game.player_hands[game.current_hand]
    if not current_hand.can_double():
        return jsonify({'success': False, 'message': 'Cannot double down'})
    
    if game.place_bet(game.bets[game.current_hand]):
        # Deal exactly one card for double down
        current_hand.add_card(game.deck.deal_card())
        
        # After double down, player must stand (no more cards)
        game.current_hand += 1
        
        if game.current_hand >= len(game.player_hands):
            game.game_phase = 'dealer'
            game.play_dealer()
        else:
            game.game_phase = 'playing'
        
        save_game_state(game)
        return jsonify({'success': True, 'game_state': game.to_dict()})
    
    return jsonify({'success': False, 'message': 'Insufficient funds'})

@app.route('/api/split', methods=['POST'])
def split():
    game = get_game_state()
    
    if game.game_phase != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    current_hand = game.player_hands[game.current_hand]
    if not current_hand.can_split():
        return jsonify({'success': False, 'message': 'Cannot split'})
    
    if game.place_bet(game.bets[game.current_hand]):
        # Create new hand with one card from current hand
        new_hand = Hand()
        new_hand.add_card(current_hand.cards.pop())
        
        # Deal one card to each hand
        current_hand.add_card(game.deck.deal_card())
        new_hand.add_card(game.deck.deal_card())
        
        # Add the new hand to the list
        game.player_hands.append(new_hand)
        
        # Stay on current hand (don't advance to next hand yet)
        # Player can now play each hand separately
        
        save_game_state(game)
        return jsonify({'success': True, 'game_state': game.to_dict()})
    
    return jsonify({'success': False, 'message': 'Insufficient funds'})

@app.route('/api/new-game', methods=['POST'])
def new_game():
    game = get_game_state()
    game.clear_hands()
    game.game_phase = 'betting'
    save_game_state(game)
    return jsonify({'success': True, 'game_state': game.to_dict()})

@app.route('/api/add-balance', methods=['POST'])
def add_balance():
    game = get_game_state()
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if amount > 0:
        game.balance += amount
        save_game_state(game)
        return jsonify({'success': True, 'game_state': game.to_dict()})
    
    return jsonify({'success': False, 'message': 'Invalid amount'})


if __name__ == '__main__':
    app.run(debug=True)
