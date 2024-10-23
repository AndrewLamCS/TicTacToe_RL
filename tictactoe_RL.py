import numpy as np  # Import NumPy for numerical operations
import pickle  # Import pickle for saving and loading models

# Define constants for the dimensions of the game board
BOARD_ROWS = 3
BOARD_COLS = 3


class State:
    def __init__(self, p1, p2):
        # Initialize the game state
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))  # Create a 3x3 board initialized to zero
        self.p1 = p1  # Player 1
        self.p2 = p2  # Player 2
        self.isEnd = False  # Flag to check if the game has ended
        self.boardHash = None  # To store the hash of the current board state
        # Initialize with Player 1's turn
        self.playerSymbol = 1

    # Get a unique hash of the current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))  # Convert the board to a string hash
        return self.boardHash

    def winner(self):
        # Check for winning conditions in rows
        for i in range(BOARD_ROWS):
            if sum(self.board[i, :]) == 3:  # Player 1 wins
                self.isEnd = True  # End the game
                return 1
            if sum(self.board[i, :]) == -3:  # Player 2 wins
                self.isEnd = True  # End the game
                return -1
        # Check for winning conditions in columns
        for i in range(BOARD_COLS):
            if sum(self.board[:, i]) == 3:  # Player 1 wins
                self.isEnd = True  # End the game
                return 1
            if sum(self.board[:, i]) == -3:  # Player 2 wins
                self.isEnd = True  # End the game
                return -1
        # Check diagonal wins
        diag_sum1 = sum([self.board[i, i] for i in range(BOARD_COLS)])  # Main diagonal
        diag_sum2 = sum([self.board[i, BOARD_COLS - i - 1] for i in range(BOARD_COLS)])  # Anti-diagonal
        diag_sum = max(abs(diag_sum1), abs(diag_sum2))  # Get the maximum absolute sum

        if diag_sum == 3:  # If a diagonal is complete
            self.isEnd = True  # End the game
            if diag_sum1 == 3 or diag_sum2 == 3:  # Player 1 wins
                return 1
            else:  # Player 2 wins
                return -1

        # Check for a tie (no available positions)
        if len(self.availablePositions()) == 0:
            self.isEnd = True  # End the game
            return 0  # Indicate a tie

        # If no winner or tie, continue the game
        self.isEnd = False
        return None

    def availablePositions(self):
        # Find all available positions on the board
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:  # Check for empty spots
                    positions.append((i, j))  # Append the position as a tuple
        return positions

    def updateState(self, position):
        # Update the board state with the player's move
        self.board[position] = self.playerSymbol  # Place the player's symbol
        # Switch to the other player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    # Only called when the game ends
    def giveReward(self):
        result = self.winner()  # Determine the outcome of the game
        # Backpropagate rewards based on the game result
        if result == 1:  # Player 1 wins
            self.p1.feedReward(1)  # Reward Player 1
            self.p2.feedReward(0)  # No reward for Player 2
        elif result == -1:  # Player 2 wins
            self.p1.feedReward(0)  # No reward for Player 1
            self.p2.feedReward(1)  # Reward Player 2
        else:  # Tie
            self.p1.feedReward(0.1)  # Small reward for Player 1
            self.p2.feedReward(0.5)  # Moderate reward for Player 2

    # Reset the game board
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))  # Clear the board
        self.boardHash = None  # Reset the board hash
        self.isEnd = False  # Set game status to not ended
        self.playerSymbol = 1  # Start with Player 1's turn

    def play(self, rounds=100):
        # Play the specified number of rounds
        for i in range(rounds):
            if i % 1000 == 0:
                print("Rounds {}".format(i))  # Print progress every 1000 rounds
            while not self.isEnd:  # Continue until the game ends
                # Player 1's turn
                positions = self.availablePositions()  # Get available positions
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)  # Player 1 chooses action
                self.updateState(p1_action)  # Update the board state with Player 1's move
                board_hash = self.getHash()  # Get the current board state hash
                self.p1.addState(board_hash)  # Record the state for Player 1

                win = self.winner()  # Check for a winner
                if win is not None:  # If the game has ended
                    self.giveReward()  # Give rewards based on the outcome
                    self.p1.reset()  # Reset Player 1's state
                    self.p2.reset()  # Reset Player 2's state
                    self.reset()  # Reset the game state
                    break  # Exit the loop

                else:
                    # Player 2's turn
                    positions = self.availablePositions()  # Get available positions
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)  # Player 2 chooses action
                    self.updateState(p2_action)  # Update the board state with Player 2's move
                    board_hash = self.getHash()  # Get the current board state hash
                    self.p2.addState(board_hash)  # Record the state for Player 2

                    win = self.winner()  # Check for a winner
                    if win is not None:  # If the game has ended
                        self.giveReward()  # Give rewards based on the outcome
                        self.p1.reset()  # Reset Player 1's state
                        self.p2.reset()  # Reset Player 2's state
                        self.reset()  # Reset the game state
                        break  # Exit the loop

    # Play against a human player
    def play2(self):
        while not self.isEnd:  # Continue until the game ends
            # Player 1's turn
            positions = self.availablePositions()  # Get available positions
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)  # Player 1 chooses action
            self.updateState(p1_action)  # Update the board state
            self.showBoard()  # Display the current board state

            win = self.winner()  # Check for a winner
            if win is not None:  # If the game has ended
                if win == 1:  # Player 1 wins
                    print(self.p1.name, "wins!")  # Announce the winner
                else:
                    print("tie!")  # Announce a tie
                self.reset()  # Reset the game
                break  # Exit the loop

            else:
                # Player 2's turn
                positions = self.availablePositions()  # Get available positions
                p2_action = self.p2.chooseAction(positions)  # Player 2 chooses action
                self.updateState(p2_action)  # Update the board state
                self.showBoard()  # Display the current board state

                win = self.winner()  # Check for a winner
                if win is not None:  # If the game has ended
                    if win == -1:  # Player 2 wins
                        print(self.p2.name, "wins!")  # Announce the winner
                    else:
                        print("tie!")  # Announce a tie
                    self.reset()  # Reset the game
                    break  # Exit the loop

    def showBoard(self):
        # Display the current state of the board
        for i in range(0, BOARD_ROWS):
            print('-------------')  # Print horizontal separator
            out = '| '  # Start building the row output
            for j in range(0, BOARD_COLS):
                if self.board[i, j] == 1:
                    token = 'x'  # Player 1's symbol
                if self.board[i, j] == -1:
                    token = 'o'  # Player 2's symbol
                if self.board[i, j] == 0:
                    token = ' '  # Empty space
                out +=
