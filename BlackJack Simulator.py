import random
import os
from typing import List, Tuple, Optional
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows support
init()

class Card:
    SUITS_COLORS = {
        '♥': Fore.RED,
        '♦': Fore.RED,
        '♠': Fore.WHITE,
        '♣': Fore.WHITE
    }
    
    def __init__(self, value: str, suit: str):
        self.value = value
        self.suit = suit
        
    def __str__(self) -> str:
        color = self.SUITS_COLORS[self.suit]
        return f"{color}{self.value}{self.suit}{Style.RESET_ALL}"
    
    def get_value(self, current_score: int = 0) -> int:
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 11 if current_score + 11 <= 21 else 1
        return int(self.value)

class Deck:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.min_cards_before_shuffle = 52  # Reshuffle when less than one deck remains
        self.create_deck()
        
    def create_deck(self):
        suits = ['♥', '♠', '♣', '♦']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(value, suit) for _ in range(self.num_decks) 
                     for suit in suits for value in values]
        self.shuffle()
        
    def shuffle(self):
        random.shuffle(self.cards)
        self.display_shuffle_animation()
        
    def display_shuffle_animation(self):
        print("\nShuffling the deck", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            import time
            time.sleep(0.3)
        print()
        
    def deal_card(self) -> Optional[Card]:
        if len(self.cards) < self.min_cards_before_shuffle:
            self.create_deck()
        if not self.cards:
            # Emergency fallback - create a new deck if somehow empty
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
                
        # Handle aces last for optimal scoring
        for ace in aces:
            score += ace.get_value(score)
            
        return score
    
    def can_split(self) -> bool:
        if len(self.cards) != 2:
            return False
        return self.cards[0].get_value() == self.cards[1].get_value()
    
    def can_double(self) -> bool:
        return len(self.cards) == 2
    
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.get_score() == 21
    
    def __str__(self) -> str:
        return ' '.join(str(card) for card in self.cards)

class Player:
    def __init__(self, balance: int = 1000):
        self.balance = balance
        self.hands: List[Hand] = [Hand()]
        self.bets: List[int] = []
        self.statistics = {
            'hands_played': 0,
            'hands_won': 0,
            'hands_lost': 0,
            'blackjacks': 0,
            'money_won': 0,
            'money_lost': 0
        }
        
    def place_bet(self, amount: int) -> bool:
        if amount <= self.balance:
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
        self.hands = [Hand()]
        self.bets = []
        self.statistics['hands_played'] += 1

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player = Player()
        self.dealer_hand = Hand()
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_logo(self):
        logo = """
╔══════════════════════════════════════════╗
║             🎲 BLACKJACK 🎲              ║
║                                          ║
║          Press ENTER to start!           ║
╚══════════════════════════════════════════╝
"""
        print(Fore.GREEN + logo + Style.RESET_ALL)
        
    def display_rules(self):
        rules = """
📋 GAME RULES:
═════════════
• Blackjack pays 3:2
• Dealer must hit on 16 and stand on 17
• Insurance pays 2:1
• Double down available on initial hand
• Split available on matching cards

🎮 CONTROLS:
═══════════
• [H] Hit   - Take another card
• [S] Stand - Keep current hand
• [D] Double- Double bet and take one card
• [P] Split - Split matching cards into two hands
"""
        print(Fore.CYAN + rules + Style.RESET_ALL)
        
    def deal_initial_cards(self):
        # Deal cards in the correct order: player, dealer, player, dealer
        self.player.hands[0].add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())
        self.player.hands[0].add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())
        
    def show_table(self, hide_dealer: bool = True):
        self.clear_screen()
        print("\n" + "═" * 40)
        print(Fore.YELLOW + "DEALER'S HAND:" + Style.RESET_ALL)
        if hide_dealer and len(self.dealer_hand.cards) > 0:
            print(f"{self.dealer_hand.cards[0]} 🂠")
        elif len(self.dealer_hand.cards) > 0:
            print(f"{self.dealer_hand} (Score: {self.dealer_hand.get_score()})")
        else:
            print("No cards")
        print("═" * 40)
            
        for i, hand in enumerate(self.player.hands):
            hand_name = "YOUR HAND" if len(self.player.hands) == 1 else f"HAND {i+1}"
            print(Fore.YELLOW + f"{hand_name}:" + Style.RESET_ALL)
            if len(hand.cards) > 0:
                print(f"{hand} (Score: {hand.get_score()})")
            else:
                print("No cards")
            print("═" * 40)
            
        print(Fore.GREEN + f"Balance: ${self.player.balance}" + Style.RESET_ALL)
    
    def get_insurance_decision(self) -> bool:
        if len(self.dealer_hand.cards) > 0 and self.dealer_hand.cards[0].value == 'A':
            while True:
                decision = input("\n🎲 Dealer shows an Ace. Would you like insurance? (y/n): ").lower()
                if decision in ['y', 'n']:
                    return decision == 'y'
        return False
    
    def handle_insurance(self, bet: int) -> bool:
        insurance_bet = bet // 2
        if self.player.place_bet(insurance_bet):
            if self.dealer_hand.is_blackjack():
                print("\n💰 Dealer has Blackjack! Insurance pays 2:1")
                self.player.win_bet(-1, 2)  # Win insurance bet at 2:1
                return True
            print("\n❌ Dealer does not have Blackjack. Insurance lost.")
            return False
        print("\n⚠️ Insufficient funds for insurance.")
        return False
    
    def play_hand(self, hand: Hand, bet: int) -> bool:
        while hand.get_score() < 21:
            self.show_table()
            
            # Build available actions
            actions = ['[H]it', '[S]tand']
            if hand.can_double():
                actions.append('[D]ouble')
            if hand.can_split():
                actions.append('S[P]lit')
                
            print(Fore.CYAN + f"\nAvailable actions: {' / '.join(actions)}" + Style.RESET_ALL)
            action = input("What would you like to do? ").lower()
            
            if action == 'h':
                hand.add_card(self.deck.deal_card())
                if hand.get_score() > 21:
                    self.show_table()
                    print(Fore.RED + f"\n💥 Bust! Score: {hand.get_score()}" + Style.RESET_ALL)
                    return False
                    
            elif action == 's':
                return True
                
            elif action == 'd' and hand.can_double():
                if self.player.place_bet(bet):  # Double the bet
                    hand.add_card(self.deck.deal_card())
                    self.show_table()
                    print(Fore.YELLOW + f"\n💰 Doubled down! Score: {hand.get_score()}" + Style.RESET_ALL)
                    return hand.get_score() <= 21
                else:
                    print(Fore.RED + "\n⚠️ Insufficient funds to double down." + Style.RESET_ALL)
                    
            elif action == 'p' and hand.can_split():
                if self.player.place_bet(bet):  # Place bet for new hand
                    new_hand = Hand()
                    new_hand.add_card(hand.cards.pop())
                    hand.add_card(self.deck.deal_card())
                    new_hand.add_card(self.deck.deal_card())
                    self.player.hands.append(new_hand)
                    return self.play_hand(hand, bet)  # Continue with current hand
                else:
                    print(Fore.RED + "\n⚠️ Insufficient funds to split." + Style.RESET_ALL)
            
            else:
                print(Fore.RED + "\n⚠️ Invalid action. Please try again." + Style.RESET_ALL)
                
        return hand.get_score() <= 21
    
    def play_dealer_hand(self):
        print(Fore.YELLOW + "\nDealer's turn:" + Style.RESET_ALL)
        self.show_table(hide_dealer=False)
        
        while self.dealer_hand.get_score() < 17:
            self.dealer_hand.add_card(self.deck.deal_card())
            print(f"Dealer hits: {self.dealer_hand} (Score: {self.dealer_hand.get_score()})")
            
        return self.dealer_hand.get_score() <= 21
    
    def display_statistics(self):
        stats = self.player.statistics
        print("\n" + "═" * 40)
        print(Fore.CYAN + "📊 GAME STATISTICS:" + Style.RESET_ALL)
        print(f"Hands Played: {stats['hands_played']}")
        print(f"Hands Won: {stats['hands_won']}")
        print(f"Hands Lost: {stats['hands_lost']}")
        print(f"Blackjacks: {stats['blackjacks']}")
        print(f"Money Won: ${stats['money_won']}")
        print(f"Money Lost: ${stats['money_lost']}")
        print(f"Net Profit: ${stats['money_won'] - stats['money_lost']}")
        print("═" * 40)
    
    def play_round(self):
        # Get bet
        while True:
            try:
                self.show_table()
                bet = int(input(Fore.GREEN + "\nPlace your bet (0 to quit): " + Style.RESET_ALL))
                if bet == 0:
                    return False
                if bet > 0 and self.player.place_bet(bet):
                    break
                print(Fore.RED + "⚠️ Invalid bet amount." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "⚠️ Please enter a valid number." + Style.RESET_ALL)
        
        # Deal initial cards
        self.deal_initial_cards()
        self.show_table()
        
        # Check for dealer blackjack possibility and offer insurance
        if self.get_insurance_decision():
            has_dealer_blackjack = self.handle_insurance(bet)
            if has_dealer_blackjack:
                if self.player.hands[0].is_blackjack():
                    print(Fore.YELLOW + "🤝 Push - both have Blackjack!" + Style.RESET_ALL)
                    self.player.push_bet()
                self.show_table(hide_dealer=False)
                return True
        
        # Check for player blackjack
        if self.player.hands[0].is_blackjack():
            print(Fore.GREEN + "\n🎉 Blackjack! You win 3:2!" + Style.RESET_ALL)
            self.player.win_bet(multiplier=1.5)
            self.player.statistics['blackjacks'] += 1
            self.show_table(hide_dealer=False)
            return True
        
        # Player's turn
        for i, hand in enumerate(self.player.hands):
            if not self.play_hand(hand, bet):
                self.player.lose_bet(i)
                continue  # Hand is bust, move to next hand
                
        # Dealer's turn if any player hands are not bust
        if any(hand.get_score() <= 21 for hand in self.player.hands):
            dealer_not_bust = self.play_dealer_hand()
            dealer_score = self.dealer_hand.get_score()
            
            # Compare hands and settle bets
            for i, hand in enumerate(self.player.hands):
                player_score = hand.get_score()
                hand_name = "" if len(self.player.hands) == 1 else f" {i+1}"
                
                if player_score > 21:
                    print(Fore.RED + f"\n💥 Hand{hand_name} is bust" + Style.RESET_ALL)
                elif not dealer_not_bust:
                    print(Fore.GREEN + f"\n🎉 Dealer busts! Hand{hand_name} wins!" + Style.RESET_ALL)
                    self.player.win_bet(i)
                elif player_score > dealer_score:
                    print(Fore.GREEN + f"\n🎉 Hand{hand_name} wins!" + Style.RESET_ALL)
                    self.player.win_bet(i)
                elif player_score < dealer_score:
                    print(Fore.RED + f"\n❌ Hand{hand_name} loses" + Style.RESET_ALL)
                    self.player.lose_bet(i)
                else:
                    print(Fore.YELLOW + f"\n🤝 Hand{hand_name} pushes" + Style.RESET_ALL)
                    self.player.push_bet(i)
        
        return True
    
    def play_game(self):
        self.clear_screen()
        self.display_logo()
        input()
        self.display_rules()
        input("\nPress Enter to continue...")
        
        while True:
            if not self.play_round():
                break
                
            self.player.clear_hands()
            self.dealer_hand = Hand()
            
            if self.player.balance <= 0:
                print(Fore.RED + "\n💔 Game Over - You're out of money!" + Style.RESET_ALL)
                break
                
            play_again = input(Fore.YELLOW + "\nWould you like to play another hand? (y/n): " + Style.RESET_ALL).lower()
            if play_again != 'y':
                break
        
        self.display_statistics()
        print(Fore.GREEN + f"\nThanks for playing! You ended with ${self.player.balance}" + Style.RESET_ALL)

if __name__ == "__main__":
    game = BlackjackGame()
    game.play_game()