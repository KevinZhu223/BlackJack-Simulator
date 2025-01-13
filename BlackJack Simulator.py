#BlackJack Simulator

import random

def create_deck(num_decks =2):
    suits = ['♥', '♠', '♣', '♦']
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    deck = [f"{card}{suit}" for suit in suits for card in cards]
    
    return deck

def shuffling(deck):
    random.shuffle(deck) 
    return deck


def deal_card(deck, hand):    
    card = deck.pop()
    
    hand.append(card)

def starting_deal(deck, player_hand, dealer_hand):    
    deal_card(deck, player_hand)
    deal_card(deck, dealer_hand)
    deal_card(deck, player_hand)
    deal_card(deck, dealer_hand)
    
    print(f"Dealer's hand: {dealer_hand[0]}")

def calc_score(hand):
    score = 0
    aces = 0
    
    for card in hand:
        value = card[:-1]
        if value in ['J', 'Q', 'K']:
            score += 10
        elif value == 'A':
            aces += 1
        else:
            score += int(value)
    
    score += aces
    while aces > 0 and score + 10 <= 21:
        score += 10
        aces -= 1
    
    return score

def player_action(deck, player_hand):
    while True:
        print(f"Your hand: {', '.join(player_hand)}")
        score = calc_score(player_hand)
        print(f"Score: {score}")
        
        #add split double and insurance later
        action = input("Hit or Stand?").strip().lower()
        
        if action == 'h':
            deal_card(deck, player_hand)
            
            if calc_score(player_hand) > 21:
                print("Bust")
                return False
        elif action == 's':
            return True
        else:
            print("Try again")
        
def dealer_action(deck, dealer_hand):
    while True:
        score = calc_score(dealer_hand)
        print(f"Dealer hand: {dealer_hand[1]} (score: {score})")
        
        if score < 17:
            deal_card(deck, dealer_hand)
        else:
            break
    return score
    #print(f"dealer has: {dealer_hand} {score}")
            
def bets(user_balance):
    while True:
        try:
            bet = int(input(f"Current Balance: ${user_balance}. Enter your bet (or 0 to stop):"))
            if bet == 0:
                print("Exiting...")
                return None
            if bet > user_balance:
                print("Bet exceeds user balance")
                continue
            if bet <= 0:
                print("Enter a valid bet size")
                continue
                
            # Display updated balance
            return bet
        except ValueError:
            print("Please enter a number")
            
            
def instructions():
    print("\nWelcome to the Blackjack Simulator!")
    print("-" * 40)
    print("The goal of Blackjack is to get a hand total as close to 21 as possible without exceeding it.")
    print("Here are the basic rules:")
    print("1. The player and the dealer are each dealt two cards to start.")
    print("   - The player's hand is fully visible.")
    print("   - The dealer's second card is hidden until their turn.")
    print("2. Cards are valued as follows:")
    print("   - Number cards (2-10) are worth their face value.")
    print("   - Face cards (J, Q, K) are worth 10 points.")
    print("   - Aces can be worth 1 or 11 points, whichever benefits the hand.")
    print("3. After the initial deal, the player chooses to:")
    print("   - Hit: Take another card.")
    print("   - Stand: End their turn.")
    print("4. If the player exceeds 21, they 'bust' and lose the round.")
    print("5. Once the player stands, the dealer's turn begins:")
    print("   - The dealer must hit until their total is at least 17.")
    print("6. The winner is determined as follows:")
    print("   - If the player’s score is higher than the dealer’s, the player wins.")
    print("   - If the dealer busts, the player wins.")
    print("   - If the player busts or the dealer’s score is higher, the dealer wins.")
    print("   - If the scores are tied, it’s a push (tie).")
    print("Press 'H' for help or space to start the game.")
    print("-" * 40)
      
    
def main():
    print("Welcome to my BlackJack Simulator")
    print("To Play: h to hit, s to stand")
    user_balance = 10000
    while True:
        choice = input("\nPress 'H' for help and instructions, otherwise Enter to start")
        if choice.lower() == 'h':
            instructions()
            continue
        elif choice == '':
            deck = create_deck()
            deck = shuffling(deck)
            
            player_hand = []
            dealer_hand = []
            
            bet = bets(user_balance)
            if bet is None:
                break
            
            starting_deal(deck, player_hand, dealer_hand)
            
            if not player_action(deck, player_hand):
                user_balance -= bet
                print(f"balance: ${user_balance}")
                if user_balance <= 0:
                    print("Game over!")
                    break
                continue
            
            player_score = calc_score(player_hand)
            dealer_score = dealer_action(deck, dealer_hand)
                        
            
            if dealer_score > 21 or player_score > dealer_score:
                print("You win!")
                user_balance += bet
            elif player_score < dealer_score:
                print("Dealer wins!")
                user_balance -= bet
            else:
                print("Push")
            
            
            print(f"Your balance: ${user_balance}")
            if user_balance <= 0:
                print("Game over!")
                break

if __name__ == "__main__":
    main()