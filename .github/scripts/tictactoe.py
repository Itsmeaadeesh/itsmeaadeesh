import sys
import os
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


REPO_OWNER = "Itsmeaadeesh"
REPO_NAME = "itsmeaadeesh"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
STATE_FILE = os.path.join(DATA_DIR, "tictactoe.json")
MSG_FILE = os.path.join(DATA_DIR, "tictactoe_last_message.txt")
README_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
        "stats": {"user_wins": 0, "bot_wins": 0, "draws": 0, "total_games": 0},
        "last_player": "",
        "game_over": False,
        "winner": None
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def check_winner(board):
    # Rows
    for r in range(3):
        if board[r][0] != " " and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0]
    # Cols
    for c in range(3):
        if board[0][c] != " " and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c]
    # Diagonals
    if board[0][0] != " " and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != " " and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    # Check if full
    is_full = all(board[r][c] != " " for r in range(3) for c in range(3))
    if is_full:
        return "DRAW"
    return None

def minimax(board, depth, is_maximizing):
    res = check_winner(board)
    if res == "O":
        return 10 - depth
    elif res == "X":
        return depth - 10
    elif res == "DRAW":
        return 0
    
    if is_maximizing:
        best_score = -1000
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "O"
                    score = minimax(board, depth + 1, False)
                    board[r][c] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = 1000
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "X"
                    score = minimax(board, depth + 1, True)
                    board[r][c] = " "
                    best_score = min(score, best_score)
        return best_score

def bot_best_move(board):
    best_score = -1000
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                board[r][c] = "O"
                score = minimax(board, 0, False)
                board[r][c] = " "
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

def render_board_markdown(state, username="Visitor"):
    board = state["board"]
    game_over = state["game_over"]
    winner = state["winner"]
    stats = state["stats"]

    # Status text
    if not game_over:
        status_text = "🟢 **Game in Progress:** Your turn! You are playing as **❌ (Player)** against **⭕ (Aadeesh AI Bot)**.<br/>👉 *Click any empty white tile (`⬜`) to make your move.*"
    elif winner == "user":
        status_text = f"🎉 **VICTORY!** Congratulations @{username}, you beat the bot! 🏆<br/>*Click 'Start New Game' below to play again.*"
    elif winner == "bot":
        status_text = "🤖 **AI Bot Won!** The neural net struck back! 🦾<br/>*Click 'Start New Game' below to try again.*"
    else:
        status_text = "🤝 **IT'S A DRAW!** Stalemate reached! Well played.<br/>*Click 'Start New Game' below to play again.*"

    md = []
    md.append("<div align=\"center\">\n")
    md.append(f"{status_text}\n")
    md.append("<br/>\n")
    
    # Table Grid
    md.append("| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |")
    md.append("| :---: | :---: | :---: |")

    for r in range(3):
        row_cells = []
        for c in range(3):
            val = board[r][c]
            if val == "X":
                row_cells.append("&nbsp;&nbsp;❌&nbsp;&nbsp;")
            elif val == "O":
                row_cells.append("&nbsp;&nbsp;⭕&nbsp;&nbsp;")
            else:
                if game_over:
                    row_cells.append("&nbsp;&nbsp;⬜&nbsp;&nbsp;")
                else:
                    move_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new?title=ttc%7C{r}%7C{c}&body=Click+%22Submit+new+issue%22+to+place+your+move+at+row+{r}%2C+col+{c}."
                    row_cells.append(f"&nbsp;&nbsp;[⬜]({move_url})&nbsp;&nbsp;")
        md.append(f"| {' | '.join(row_cells)} |")

    md.append("\n<br/>\n")
    reset_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new?title=ttc%7Creset&body=Click+%22Submit+new+issue%22+to+reset+the+game+board."
    md.append(f"<p align=\"center\">\n  <a href=\"{reset_url}\">\n    <img src=\"https://img.shields.io/badge/🔄_Start_New_Game-00F2FE?style=for-the-badge&logoColor=black\" alt=\"Restart Game\" />\n  </a>\n</p>\n")
    
    md.append("<p align=\"center\">")
    md.append(f"<b>🎮 Total Games:</b> {stats['total_games']} &nbsp;|&nbsp; ")
    md.append(f"<b>🏆 Visitor Wins:</b> {stats['user_wins']} &nbsp;|&nbsp; ")
    md.append(f"<b>🤖 Bot Wins:</b> {stats['bot_wins']} &nbsp;|&nbsp; ")
    md.append(f"<b>🤝 Draws:</b> {stats['draws']}")
    md.append("</p>\n")
    md.append("</div>")

    return "\n".join(md)

def update_readme(board_markdown):
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"(<!-- TIC-TAC-TOE:START -->)(.*?)(<!-- TIC-TAC-TOE:END -->)", re.DOTALL)
    if pattern.search(content):
        new_content = pattern.sub(f"\\1\n\n{board_markdown}\n\n\\3", content)
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    if len(sys.argv) < 2:
        title = "ttc|init"
        user = "Guest"
    else:
        title = sys.argv[1].strip()
        user = sys.argv[2].strip() if len(sys.argv) > 2 else "Guest"

    state = load_state()
    message = "Thanks for playing! Check the updated board on the profile."

    if title == "ttc|reset":
        state["board"] = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        state["game_over"] = False
        state["winner"] = None
        state["last_player"] = user
        message = f"🔄 Game has been reset by @{user}! It's your turn to make the first move."
    elif title.startswith("ttc|") and len(title.split("|")) == 3:
        parts = title.split("|")
        try:
            r, c = int(parts[1]), int(parts[2])
            if state["game_over"]:
                message = "⚠️ This game is already over! Click [Start New Game] on the profile to play again."
            elif 0 <= r < 3 and 0 <= c < 3:
                if state["board"][r][c] != " ":
                    message = f"⚠️ That tile ({r}, {c}) is already taken! Choose an empty [⬜] tile."
                else:
                    # User plays X
                    state["board"][r][c] = "X"
                    state["last_player"] = user
                    winner = check_winner(state["board"])

                    if winner == "X":
                        state["game_over"] = True
                        state["winner"] = "user"
                        state["stats"]["user_wins"] += 1
                        state["stats"]["total_games"] += 1
                        message = f"🎉 Incredible! @{user} placed ❌ at ({r},{c}) and WON the game! 🏆"
                    elif winner == "DRAW":
                        state["game_over"] = True
                        state["winner"] = "draw"
                        state["stats"]["draws"] += 1
                        state["stats"]["total_games"] += 1
                        message = f"🤝 Game ended in a DRAW after @{user}'s move at ({r},{c})."
                    else:
                        # Bot plays O
                        bmove = bot_best_move(state["board"])
                        if bmove:
                            br, bc = bmove
                            state["board"][br][bc] = "O"
                            bot_winner = check_winner(state["board"])
                            if bot_winner == "O":
                                state["game_over"] = True
                                state["winner"] = "bot"
                                state["stats"]["bot_wins"] += 1
                                state["stats"]["total_games"] += 1
                                message = f"🤖 @{user} played at ({r},{c}). Aadeesh AI Bot countered at ({br},{bc}) and WON! 🦾"
                            elif bot_winner == "DRAW":
                                state["game_over"] = True
                                state["winner"] = "draw"
                                state["stats"]["draws"] += 1
                                state["stats"]["total_games"] += 1
                                message = f"🤝 @{user} played at ({r},{c}). Bot placed at ({br},{bc}). It's a DRAW!"
                            else:
                                message = f"⚡ @{user} placed ❌ at ({r},{c}). Bot countered with ⭕ at ({br},{bc}). Your turn!"
        except Exception as e:
            message = f"Error processing move: {str(e)}"
    
    save_state(state)
    board_md = render_board_markdown(state, user)
    update_readme(board_md)

    with open(MSG_FILE, "w", encoding="utf-8") as f:
        f.write(message)

    print(message)

if __name__ == "__main__":
    main()
