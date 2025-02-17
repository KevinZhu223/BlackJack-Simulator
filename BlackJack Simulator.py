#BlackJack Simulator
#Need to check why dealer keeps getting dealt the same value card.
#Implement double, split, and insurance
#other bug fixes
#when player gets 21 do not give option to hit or stand
#implement shuffle when deck is done

import random
#Should only be called once
def create_deck(num_decks =2):
    suits = ['♥', '♠', '♣', '♦']
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    deck = [f"{card}{suit}" for suit in suits for card in cards] * num_decks
    return deck

#This should be called at the start and after 10 cards are left
#In the deck since live BlackJack does not shuffle after each hand.
def shuffling(deck):
    random.shuffle(deck) 
    return deck

def check_and_reshuffle(deck, num_decks = 2, threshold = 10):
    if len(deck) < threshold:
        print("Reshuffling") # maybe remove this print statment later
        new_deck = create_deck(num_decks)
        shuffling(new_deck)
        deck.extend(new_deck)
    return deck

#Should take the top card from the deck and give it to the correct person
def deal_card(deck, hand):
    check_and_reshuffle(deck)    
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
        card1_value = 10 if player_hand[0][:-1] in ['J', 'Q', 'K'] else player_hand[0][:-1]
        card2_value = 10 if player_hand[1][:-1] in ['J', 'Q', 'K'] else player_hand[1][:-1]
        
        if(card1_value == card2_value):
            action = input("Hit, Stand, or Split? (h/s/x)").strip().lower()
        else:
            action = input("Hit or Stand? (h/s)").strip().lower()
        
        if action == 'h':
            deal_card(deck, player_hand)
            score = calc_score(player_hand)
            if score > 21:
                print(f"{', '.join(player_hand)}")
                print(f"Score: {score}")
                print("Bust")
                return False, False
        elif action == 's':
            return True, False
        elif action == 'x':
            handle_split(deck, player_hand)
        else:
            print("Try again")
            
def play_hand(deck, hand, hand_name):
    while True:
        print(f"{hand_name}: {', '.join(hand)} (Score: {calc_score(hand)})")
        action = input("Hit or Stand? (h/s) ").strip().lower()
        
        if action == 'h':
            deal_card(deck, hand)
            score = calc_score(hand)
            if score > 21:
                print(f"{hand_name}: {', '.join(hand)} (Score: {score}) - Bust!")
                return False
        elif action == 's':
            return True
        else:
            print("Try Again")

     
#Helper for when splitting hands
def handle_split(deck, player_hand):
    first_hand = [player_hand[0]]
    second_hand = [player_hand[1]]
            
    deal_card(deck, first_hand)
    deal_card(deck, second_hand)
            
    first_result = play_hand(deck, first_hand, "First Hand")  # Play first hand
    
    second_result = play_hand(deck, second_hand, "Second Hand")  # Play second hand

    return first_result, second_result


def dealer_action(deck, dealer_hand):
    while True:
        score = calc_score(dealer_hand)
        print(f"Dealer hand: {', '.join(dealer_hand)} (score: {score})")
        
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
    print("To Play: h to hit, s to stand, and x to split")
    deck = create_deck()
    deck = shuffling(deck)
    user_balance = 10000
    while True:
        check_and_reshuffle(deck)
        choice = input("\nPress 'H' for help and instructions, otherwise Enter to start")
        if choice.lower() == 'h':
            instructions()
            continue
        elif choice == '':
            player_hand = []
            dealer_hand = [] 
            
            bet = bets(user_balance)
            if bet is None:
                break
            
            starting_deal(deck, player_hand, dealer_hand)
            if calc_score(player_hand) == 21:
                print(f"Your hand: {', '.join(player_hand)}")
                print("BlackJack!")
                user_balance += int(1.5 * bet)
                print(f"Your balance: ${user_balance}")
                continue
            
            player_stands, player_split = player_action(deck, player_hand)
                       
            if not player_stands and not player_split:
                user_balance -= bet
                print(f"Balance: ${user_balance}")
                if user_balance <= 0:
                    print("Game over!")
                    break
                continue
            
            dealer_score = dealer_action(deck, dealer_hand)

            if player_split:
                first_hand, second_hand = player_stands
                first_score = calc_score(first_hand)
                second_score = calc_score(second_hand)
                
                if dealer_score > 21:
                    print("Dealer Busts! Both hands win.")
                    user_balance += bet * 2
                else:
                    if first_score > 21:
                        user_balance -= bet
                    elif first_score > dealer_score:
                        user_balance += bet
                    elif first_score < dealer_score:
                        user_balance -= bet
                    
                    if second_score > 21:
                        user_balance -= bet
                    elif second_score > dealer_score:
                        user_balance += bet
                    elif second_score < dealer_score:
                        user_balance -= bet
            else:
                player_score = calc_score(player_hand)
                if dealer_score > 21 or player_score > dealer_score:
                    print("You win")
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