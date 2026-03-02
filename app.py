"""
BlackJack Card-Counting Trainer — Flask back-end
=================================================
Features
--------
* Full blackjack game engine (hit, stand, double, split, insurance)
* Hi-Lo running / true count tracked server-side
* Learn-mode endpoints: count-check quiz, basic-strategy hints, shoe info
* In-memory game-state stored as live Python objects (no lossy serialisation)
"""

from flask import Flask, render_template, request, jsonify, session
import random
import math
from typing import List, Optional

app = Flask(__name__, static_folder="static")
app.secret_key = "blackjack_counting_trainer_2026"

# ---------------------------------------------------------------------------
# In-memory game storage  (production would use Redis / DB)
# ---------------------------------------------------------------------------
game_states: dict = {}

# ---------------------------------------------------------------------------
# Hi-Lo card values
# ---------------------------------------------------------------------------
HILO = {
    "2": 1, "3": 1, "4": 1, "5": 1, "6": 1,
    "7": 0, "8": 0, "9": 0,
    "10": -1, "J": -1, "Q": -1, "K": -1, "A": -1,
}

# ===========================  CARD / DECK / HAND  ==========================

class Card:
    _SUIT_NAMES = {"♥": "hearts", "♦": "diamonds", "♠": "spades", "♣": "clubs"}

    def __init__(self, value: str, suit: str):
        self.value = value
        self.suit = suit
        self.suit_name = self._SUIT_NAMES.get(suit, suit)

    def numeric(self) -> int:
        """Base numeric value (Ace → 11, face → 10)."""
        if self.value in ("J", "Q", "K"):
            return 10
        if self.value == "A":
            return 11
        return int(self.value)

    def hilo(self) -> int:
        return HILO.get(self.value, 0)

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "suit": self.suit,
            "suit_name": self.suit_name,
            "display": f"{self.value}{self.suit}",
        }


class Deck:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.total_cards = num_decks * 52
        self.cut_position = int(self.total_cards * 0.25)  # reshuffle at 25 % left
        self.cards: List[Card] = []
        self._build()

    def _build(self):
        suits = ["♥", "♠", "♣", "♦"]
        values = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        self.cards = [
            Card(v, s) for _ in range(self.num_decks) for s in suits for v in values
        ]
        random.shuffle(self.cards)

    def needs_shuffle(self) -> bool:
        return len(self.cards) <= self.cut_position

    def deal(self) -> Card:
        if not self.cards:
            self._build()
        return self.cards.pop()

    def remaining(self) -> int:
        return len(self.cards)

    def decks_remaining(self) -> float:
        return len(self.cards) / 52.0


class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def add(self, card: Card):
        self.cards.append(card)

    def score(self) -> int:
        total = 0
        aces = 0
        for c in self.cards:
            if c.value == "A":
                aces += 1
                total += 11
            else:
                total += c.numeric()
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_soft(self) -> bool:
        total = 0
        aces = 0
        for c in self.cards:
            if c.value == "A":
                aces += 1
                total += 11
            else:
                total += c.numeric()
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return aces > 0

    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].numeric() == self.cards[1].numeric()

    def can_double(self) -> bool:
        return len(self.cards) == 2

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.score() == 21

    def to_dict(self) -> dict:
        return {
            "cards": [c.to_dict() for c in self.cards],
            "score": self.score(),
            "is_soft": self.is_soft(),
            "can_split": self.can_split(),
            "can_double": self.can_double(),
            "is_blackjack": self.is_blackjack(),
        }


# ===========================  BASIC STRATEGY  =============================

def basic_strategy(hand: Hand, dealer_up: Card) -> str:
    """Return the optimal basic-strategy action: hit / stand / double / split."""
    s = hand.score()
    soft = hand.is_soft()
    pair = hand.can_split()
    dbl = hand.can_double()
    d = dealer_up.numeric()          # Ace → 11

    # ---- pairs ----
    if pair:
        v = hand.cards[0].numeric()
        if v == 11:               return "split"   # always split Aces
        if v == 8:                return "split"   # always split 8s
        if v == 10:               pass             # never split 10s → fall through
        elif v == 5:              pass             # never split 5s → treat as hard 10
        elif v == 4:
            if d in (5, 6):       return "split"
        elif v in (2, 3, 7):
            if d <= 7:            return "split"
        elif v == 6:
            if d <= 6:            return "split"
        elif v == 9:
            if d <= 9 and d != 7: return "split"
            if d == 7:            return "stand"

    # ---- soft totals ----
    if soft:
        if s >= 20:               return "stand"
        if s == 19:
            if dbl and d == 6:    return "double"
            return "stand"
        if s == 18:
            if dbl and d in (3,4,5,6): return "double"
            if d in (2, 7, 8):         return "stand"
            return "hit"
        if s == 17:
            if dbl and d in (3,4,5,6): return "double"
            return "hit"
        if s in (15, 16):
            if dbl and d in (4,5,6):   return "double"
            return "hit"
        if s in (13, 14):
            if dbl and d in (5,6):     return "double"
            return "hit"
        return "hit"

    # ---- hard totals ----
    if s >= 17:                   return "stand"
    if 13 <= s <= 16:
        return "stand" if d <= 6 else "hit"
    if s == 12:
        return "stand" if d in (4,5,6) else "hit"
    if s == 11:
        return "double" if dbl else "hit"
    if s == 10:
        return "double" if dbl and d <= 9 else "hit"
    if s == 9:
        return "double" if dbl and 3 <= d <= 6 else "hit"
    return "hit"                  # 8 or below


# ===========================  GAME STATE  =================================

class GameState:
    def __init__(self):
        self.deck = Deck()
        self.player_hands: List[Hand] = [Hand()]
        self.dealer_hand = Hand()
        self.balance = 1000
        self.bets: List[int] = []
        self.current_hand = 0
        self.phase = "betting"            # betting | playing | dealer | finished
        self.insurance_bet = 0
        self.insurance_decided = False
        self.running_count = 0
        self.hands_since_shuffle = 0
        self.hole_counted = False
        self.learn_mode = False
        self.show_count = False
        self.results: list = []           # per-hand outcome list
        self.stats = dict(
            played=0, won=0, lost=0, pushed=0, blackjacks=0,
            money_won=0, money_lost=0,
        )
        self.counting = dict(
            checks=0, correct=0, close=0,
            strat_checks=0, strat_correct=0,
        )

    # ---- betting helpers ----
    def bet(self, amount: int) -> bool:
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.bets.append(amount)
            return True
        return False

    def _win(self, i: int, mult: float = 1.0):
        if i < len(self.bets):
            w = int(self.bets[i] * (1 + mult))
            self.balance += w
            self.stats["won"] += 1
            self.stats["money_won"] += w - self.bets[i]

    def _lose(self, i: int):
        if i < len(self.bets):
            self.stats["lost"] += 1
            self.stats["money_lost"] += self.bets[i]

    def _push(self, i: int):
        if i < len(self.bets):
            self.balance += self.bets[i]
            self.stats["pushed"] += 1

    # ---- counting helpers ----
    def count(self, card: Card):
        self.running_count += card.hilo()

    def true_count(self) -> float:
        dr = self.deck.decks_remaining()
        return round(self.running_count / dr, 1) if dr > 0.25 else float(self.running_count)

    def reveal_hole(self):
        if not self.hole_counted and len(self.dealer_hand.cards) > 1:
            self.count(self.dealer_hand.cards[1])
            self.hole_counted = True

    def maybe_shuffle(self) -> bool:
        if self.deck.needs_shuffle():
            self.deck._build()
            self.running_count = 0
            self.hands_since_shuffle = 0
            return True
        return False

    # ---- hand flow ----
    def new_hand(self):
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.bets.clear()
        self.current_hand = 0
        self.insurance_bet = 0
        self.insurance_decided = False
        self.hole_counted = False
        self.results.clear()
        self.stats["played"] += 1
        self.hands_since_shuffle += 1

    def advance(self):
        """Move to next split hand or trigger dealer play."""
        self.current_hand += 1
        if self.current_hand >= len(self.player_hands):
            if any(h.score() <= 21 for h in self.player_hands):
                self.phase = "dealer"
                self._play_dealer()
            else:
                self.reveal_hole()
                self.phase = "finished"

    def _play_dealer(self):
        self.reveal_hole()
        while self.dealer_hand.score() < 17:
            c = self.deck.deal()
            self.dealer_hand.add(c)
            self.count(c)
        ds = self.dealer_hand.score()
        bust = ds > 21
        for i, h in enumerate(self.player_hands):
            ps = h.score()
            if ps > 21:
                continue                           # already recorded during play
            if bust:
                self._win(i);  self.results.append(dict(r="win",  h=i, msg="Dealer busts!"))
            elif ps > ds:
                self._win(i);  self.results.append(dict(r="win",  h=i, msg=f"{ps} beats {ds}"))
            elif ps < ds:
                self._lose(i); self.results.append(dict(r="lose", h=i, msg=f"{ps} vs {ds}"))
            else:
                self._push(i); self.results.append(dict(r="push", h=i, msg=f"Both {ps}"))
        self.phase = "finished"

    # ---- serialisation ----
    def to_dict(self) -> dict:
        d = dict(
            player_hands=[h.to_dict() for h in self.player_hands],
            dealer_hand=self.dealer_hand.to_dict(),
            balance=self.balance,
            bets=self.bets,
            current_hand=self.current_hand,
            game_phase=self.phase,
            insurance_bet=self.insurance_bet,
            insurance_decided=self.insurance_decided,
            statistics=self.stats,
            last_hand_results=self.results,
            learn_mode=self.learn_mode,
            show_count=self.show_count,
            deck_info=dict(
                cards_remaining=self.deck.remaining(),
                total_cards=self.deck.total_cards,
                decks_remaining=round(self.deck.decks_remaining(), 1),
                num_decks=self.deck.num_decks,
                penetration=round(
                    (1 - self.deck.remaining() / self.deck.total_cards) * 100, 1
                ),
            ),
            counting_stats=self.counting,
            hands_since_shuffle=self.hands_since_shuffle,
        )
        if self.show_count:
            d["count_info"] = dict(
                running_count=self.running_count,
                true_count=self.true_count(),
            )
        return d


# ===========================  SESSION HELPER  ==============================

def _game() -> GameState:
    sid = session.setdefault("sid", "default")
    if sid not in game_states:
        game_states[sid] = GameState()
    return game_states[sid]


# ===========================  ROUTES  ======================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/game-state")
def api_state():
    return jsonify(_game().to_dict())


@app.route("/api/place-bet", methods=["POST"])
def api_place_bet():
    g = _game()
    amt = request.get_json().get("bet", 0)
    if g.phase != "betting":
        return jsonify(success=False, message="Not in betting phase")
    reshuffled = g.maybe_shuffle()
    if not g.bet(amt):
        return jsonify(success=False, message="Invalid bet amount")

    g.phase = "playing"
    # deal: player-dealer-player-dealer
    p1 = g.deck.deal(); g.player_hands[0].add(p1); g.count(p1)
    du = g.deck.deal(); g.dealer_hand.add(du);      g.count(du)
    p2 = g.deck.deal(); g.player_hands[0].add(p2); g.count(p2)
    dh = g.deck.deal(); g.dealer_hand.add(dh)       # hole card — NOT counted yet

    if g.player_hands[0].is_blackjack():
        g.reveal_hole()
        g.phase = "finished"
        if g.dealer_hand.is_blackjack():
            g._push(0)
            g.results = [dict(r="push", h=0, msg="Both Blackjack!")]
        else:
            g._win(0, 1.5)
            g.stats["blackjacks"] += 1
            g.results = [dict(r="blackjack", h=0, msg="Blackjack pays 3:2!")]

    out = g.to_dict()
    out["reshuffled"] = reshuffled
    return jsonify(success=True, game_state=out)


@app.route("/api/insurance", methods=["POST"])
def api_insurance():
    g = _game()
    take = request.get_json().get("insurance", False)
    if g.phase != "playing":
        return jsonify(success=False, message="Not in playing phase")
    result = None
    if take and g.dealer_hand.cards and g.dealer_hand.cards[0].value == "A":
        ins = g.bets[0] // 2
        if 0 < ins <= g.balance:
            g.balance -= ins
            g.insurance_bet = ins
            if g.dealer_hand.is_blackjack():
                g.balance += ins * 3
                g.reveal_hole()
                result = "win"
            else:
                result = "lose"
    g.insurance_decided = True
    return jsonify(success=True, game_state=g.to_dict(), insurance_result=result)


@app.route("/api/hit", methods=["POST"])
def api_hit():
    g = _game()
    if g.phase != "playing":
        return jsonify(success=False, message="Not in playing phase")
    h = g.player_hands[g.current_hand]
    c = g.deck.deal(); h.add(c); g.count(c)
    if h.score() > 21:
        g._lose(g.current_hand)
        g.results.append(dict(r="bust", h=g.current_hand, msg=f"Bust with {h.score()}!"))
        g.advance()
    elif h.score() == 21:
        g.advance()
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/stand", methods=["POST"])
def api_stand():
    g = _game()
    if g.phase != "playing":
        return jsonify(success=False, message="Not in playing phase")
    g.advance()
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/double", methods=["POST"])
def api_double():
    g = _game()
    if g.phase != "playing":
        return jsonify(success=False, message="Not in playing phase")
    h = g.player_hands[g.current_hand]
    if not h.can_double():
        return jsonify(success=False, message="Cannot double down")
    b = g.bets[g.current_hand]
    if b > g.balance:
        return jsonify(success=False, message="Insufficient funds")
    g.balance -= b
    g.bets[g.current_hand] *= 2
    c = g.deck.deal(); h.add(c); g.count(c)
    if h.score() > 21:
        g._lose(g.current_hand)
        g.results.append(dict(r="bust", h=g.current_hand, msg=f"Bust on double!"))
    g.advance()
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/split", methods=["POST"])
def api_split():
    g = _game()
    if g.phase != "playing":
        return jsonify(success=False, message="Not in playing phase")
    h = g.player_hands[g.current_hand]
    if not h.can_split():
        return jsonify(success=False, message="Cannot split")
    b = g.bets[g.current_hand]
    if b > g.balance:
        return jsonify(success=False, message="Insufficient funds")
    g.balance -= b
    g.bets.insert(g.current_hand + 1, b)
    nh = Hand()
    nh.add(h.cards.pop())
    c1 = g.deck.deal(); h.add(c1);  g.count(c1)
    c2 = g.deck.deal(); nh.add(c2); g.count(c2)
    g.player_hands.insert(g.current_hand + 1, nh)
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/new-game", methods=["POST"])
def api_new_game():
    g = _game()
    g.new_hand()
    g.phase = "betting"
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/add-balance", methods=["POST"])
def api_add_balance():
    g = _game()
    amt = request.get_json().get("amount", 0)
    if amt > 0:
        g.balance += amt
        return jsonify(success=True, game_state=g.to_dict())
    return jsonify(success=False, message="Invalid amount")


@app.route("/api/reset", methods=["POST"])
def api_reset():
    sid = session.get("sid", "default")
    game_states[sid] = GameState()
    return jsonify(success=True, game_state=game_states[sid].to_dict())


# ========================  LEARN-MODE ENDPOINTS  ===========================

@app.route("/api/toggle-learn-mode", methods=["POST"])
def api_toggle_learn():
    g = _game()
    g.learn_mode = request.get_json().get("learn_mode", not g.learn_mode)
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/toggle-count-display", methods=["POST"])
def api_toggle_count():
    g = _game()
    g.show_count = request.get_json().get("show_count", not g.show_count)
    return jsonify(success=True, game_state=g.to_dict())


@app.route("/api/check-count", methods=["POST"])
def api_check_count():
    g = _game()
    guess = request.get_json().get("count", 0)
    actual = g.running_count
    tc = g.true_count()
    g.counting["checks"] += 1
    diff = abs(guess - actual)
    if diff == 0:
        g.counting["correct"] += 1
        res, msg = "correct", f"Perfect! The running count is {actual}."
    elif diff <= 1:
        g.counting["close"] += 1
        res, msg = "close", f"Close! You said {guess}, actual is {actual}."
    else:
        res, msg = "wrong", f"Off by {diff}. You said {guess}, actual is {actual}."
    tot = g.counting["checks"]
    acc = round(g.counting["correct"] / tot * 100, 1) if tot else 0
    return jsonify(
        success=True, result=res, message=msg,
        actual_running_count=actual, true_count=tc,
        player_guess=guess, accuracy=acc,
        counting_stats=g.counting,
    )


@app.route("/api/check-strategy", methods=["POST"])
def api_check_strategy():
    g = _game()
    action = request.get_json().get("action", "")
    if g.phase != "playing" or not g.player_hands:
        return jsonify(success=False, message="No active hand")
    rec = basic_strategy(g.player_hands[g.current_hand], g.dealer_hand.cards[0])
    g.counting["strat_checks"] += 1
    ok = action.lower() == rec.lower()
    if ok:
        g.counting["strat_correct"] += 1
    return jsonify(
        success=True, is_correct=ok,
        recommendation=rec, player_action=action,
        counting_stats=g.counting,
    )


@app.route("/api/get-hint", methods=["POST"])
def api_get_hint():
    g = _game()
    if g.phase != "playing" or not g.player_hands:
        return jsonify(success=False, message="No active hand")
    h = g.player_hands[g.current_hand]
    du = g.dealer_hand.cards[0]
    rec = basic_strategy(h, du)
    tc = g.true_count()
    if tc >= 2:
        adv = f"True count is +{tc} (favorable) — consider raising bets."
    elif tc <= -2:
        adv = f"True count is {tc} (unfavorable) — consider minimum bets."
    else:
        adv = f"True count is {tc} (neutral) — play basic strategy."
    return jsonify(
        success=True, recommendation=rec, count_advice=adv,
        player_score=h.score(), dealer_shows=du.value, is_soft=h.is_soft(),
    )


@app.route("/api/new-shoe", methods=["POST"])
def api_new_shoe():
    g = _game()
    if g.phase != "betting":
        return jsonify(success=False, message="Can only shuffle between hands")
    g.deck._build()
    g.running_count = 0
    g.hands_since_shuffle = 0
    return jsonify(success=True, game_state=g.to_dict(), message="New shoe shuffled!")


if __name__ == "__main__":
    app.run(debug=True)
