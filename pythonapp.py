import tkinter as tk  # Tkinter is used for the GUI of the application
from tkinter import messagebox  # For displaying message boxes to the user
import random  # For generating random numbers in the game
import mysql.connector  # For connecting to the MySQL database to store user data


class GuessingGameApp:
    def __init__(self, root):
        """
        Initializes the main game application, including GUI setup, database connection, and initial state.
        """
        self.root = root
        self.root.title("Guess the Number Game")  # Set the window title
        self.root.geometry("500x400")  # Set the window size
        self.root.configure(bg="#f0f8ff")  # Set the background color of the window

        # Game state variables
        self.low = 1  # Lowest number in the guessing range
        self.high = 1000  # Highest number in the guessing range
        self.number = None  # The target number to guess (generated randomly)
        self.max_attempts = 10  # Maximum attempts allowed in "Game Mode"
        self.guesses = 0  # Counter for the number of guesses made
        self.remaining_attempts = 0  # Remaining attempts for "Game Mode"
        self.current_mode = None  # The current game mode (either "Practice" or "Game")

        # Database connection setup
        self.db = self.connect_to_db()  # Connect to the database
        self.create_users_table()  # Create the users table if it doesn't exist

        # Create login widgets (GUI elements)
        self.create_login_widgets()

    def connect_to_db(self):
        """
        Connects to the MySQL database.
        """
        return mysql.connector.connect(
            host="localhost",
            user="root",  # MySQL username
            password="@Viper0310",  # MySQL password
            database="guessing_game"  # Name of the database
        )

    def create_users_table(self):
        """
        Creates a 'users' table in the database if it does not already exist.
        The table stores usernames and their corresponding passwords.
        """
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        self.db.commit()  # Commit the changes to the database

    def create_login_widgets(self):
        """
        Creates the widgets for the login and sign-up screen (username, password fields, and buttons).
        """
        self.login_frame = tk.Frame(self.root, bg="#f0f8ff")  # Frame to hold login widgets
        self.login_frame.pack(pady=20)  # Pack the frame into the window

        # Label for the login heading
        tk.Label(self.login_frame, text="Login or Sign Up", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=10)

        # Username label and entry field
        tk.Label(self.login_frame, text="Username:", font=("Arial", 12), bg="#f0f8ff").pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)

        # Password label and entry field (password is hidden with '*')
        tk.Label(self.login_frame, text="Password:", font=("Arial", 12), bg="#f0f8ff").pack(pady=5)
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 12), show="*", width=25)
        self.password_entry.pack(pady=5)

        # Login button that calls the 'login' method
        tk.Button(
            self.login_frame, text="Login", font=("Arial", 12), bg="#87ceeb", fg="white", command=self.login
        ).pack(pady=5)

        # Sign-up button that calls the 'sign_up' method
        tk.Button(
            self.login_frame, text="Sign Up", font=("Arial", 12), bg="#4682b4", fg="white", command=self.sign_up
        ).pack(pady=5)

    def login(self):
        """
        Handles the login logic: checks the username and password against the database.
        If successful, proceeds to the game rules screen.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()  # Fetch the result of the query

        if result:
            messagebox.showinfo("Login Success", f"Welcome back, {username}!")  # Show success message
            self.login_frame.pack_forget()  # Hide the login frame
            self.create_rules_widgets()  # Proceed to game rules screen
            self.rules_frame.pack(pady=20)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")  # Show error if login fails

    def sign_up(self):
        """
        Handles the sign-up logic: inserts the username and password into the database if valid.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Sign Up Failed", "Please enter both username and password.")  # Show error if input is invalid
            return

        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.db.commit()  # Commit the changes to the database
            messagebox.showinfo("Sign Up Success", "Your account has been created. Please log in.")  # Show success message
            self.username_entry.delete(0, tk.END)  # Clear the username and password fields
            self.password_entry.delete(0, tk.END)
        except mysql.connector.IntegrityError:
            messagebox.showerror("Sign Up Failed", "Username already exists.")  # Show error if username already exists

    def create_rules_widgets(self):
        """
        Creates the widgets for the game rules screen and displays the rules of the game.
        """
        self.rules_frame = tk.Frame(self.root, bg="#f0f8ff")

        # Label for the rules heading
        tk.Label(self.rules_frame, text="Rules of the Game", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=10)

        # The rules text
        rules = (
            "1. Guess the correct number within the range.\n"
            "2. Practice Mode: Unlimited attempts.\n"
            "3. Game Mode: Limited attempts.\n"
            "4. Feedback after each guess:\n"
            "   - Too high or too low.\n"
            "5. Range adjusts dynamically in Game Mode.\n"
            "6. Have fun!"
        )
        tk.Label(self.rules_frame, text=rules, font=("Arial", 12), bg="#f0f8ff", justify="left", wraplength=450).pack(pady=10)

        # Button to proceed to the mode selection screen
        tk.Button(
            self.rules_frame, text="Next", font=("Arial", 12), bg="#87ceeb", fg="white", command=self.go_to_mode_selection
        ).pack(pady=20)

    def go_to_mode_selection(self):
        """
        Hides the rules frame and displays the mode selection screen.
        """
        self.rules_frame.pack_forget()
        self.create_mode_widgets()  # Create mode selection widgets
        self.mode_frame.pack(pady=20)

    def create_mode_widgets(self):
        """
        Creates the widgets for the mode selection screen, where the user chooses between Practice Mode and Game Mode.
        """
        self.mode_frame = tk.Frame(self.root, bg="#f0f8ff")
        tk.Label(self.mode_frame, text="Choose Your Mode", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=10)

        # Button for Practice Mode
        tk.Button(
            self.mode_frame, text="Practice Mode", font=("Arial", 12), bg="#87ceeb", fg="white", command=self.start_Practice_mode
        ).pack(pady=10)

        # Button for Game Mode
        tk.Button(
            self.mode_frame, text="Game Mode", font=("Arial", 12), bg="#4682b4", fg="white", command=self.start_Game_mode
        ).pack(pady=10)

    def start_Practice_mode(self):
        """
        Starts the game in Practice Mode (unlimited attempts).
        """
        self.current_mode = "Practice"
        self.start_game()  # Start the game

    def start_Game_mode(self):
        """
        Starts the game in Game Mode (limited attempts).
        """
        self.current_mode = "Game"
        self.start_game()  # Start the game

    def start_game(self):
        """
        Initializes the game variables and starts the game by displaying the game screen.
        """
        self.number = random.randint(self.low, self.high)  # Randomly select a number to guess
        self.guesses = 0  # Reset the guess count
        self.remaining_attempts = self.max_attempts  # Reset remaining attempts for Game Mode

        self.create_game_widgets()  # Create widgets for the game screen
        self.feedback.config(text="")  # Clear feedback text
        self.remaining_label.config(text="")  # Clear remaining attempts label
        self.instructions.config(
            text=f"Guess a number between {self.low} and {self.high}. "
                 + ("Unlimited attempts!" if self.current_mode == "Practice" else f"You have {self.max_attempts} attempts.")
        )

        # Hide the mode selection frame and show the game screen
        self.mode_frame.pack_forget()
        self.game_frame.pack(pady=20)

    def create_game_widgets(self):
        """
        Creates the widgets for the game screen, including input fields, feedback labels, and buttons.
        """
        self.game_frame = tk.Frame(self.root, bg="#f0f8ff")

        # Instructions label
        self.instructions = tk.Label(self.game_frame, text="", font=("Arial", 14), bg="#f0f8ff")
        self.instructions.pack(pady=10)

        # Guess input field
        self.guess_entry = tk.Entry(self.game_frame, font=("Arial", 12), width=20)
        self.guess_entry.pack(pady=5)

        # Submit button for submitting a guess
        self.submit_button = tk.Button(
            self.game_frame, text="Submit Guess", font=("Arial", 12), bg="#87ceeb", fg="white", command=self.check_guess
        )
        self.submit_button.pack(pady=10)

        # Feedback label for showing the result of the guess
        self.feedback = tk.Label(self.game_frame, text="", font=("Arial", 12), bg="#f0f8ff", fg="blue")
        self.feedback.pack(pady=10)

        # Remaining attempts label for Game Mode
        self.remaining_label = tk.Label(self.game_frame, text="", font=("Arial", 12), bg="#f0f8ff", fg="red")
        self.remaining_label.pack(pady=5)

    def check_guess(self):
        """
        Checks the user's guess and provides feedback. Updates the game state accordingly.
        """
        try:
            guess = int(self.guess_entry.get())  # Get the guess from the input field
            if guess < self.low or guess > self.high:  # Check if the guess is within the valid range
                self.feedback.config(text=f"Guess must be between {self.low} and {self.high}. Try again!")
                return

            self.guesses += 1  # Increment guess counter

            if self.current_mode == "Game":
                self.remaining_attempts -= 1  # Decrease remaining attempts in Game Mode

            if guess < self.number:  # If the guess is too low
                self.low = max(self.low, guess + 1)
                self.feedback.config(
                    text=f"{guess} is too low. The number is between {self.low} and {self.high}. Try again!"
                )
            elif guess > self.number:  # If the guess is too high
                self.high = min(self.high, guess - 1)
                self.feedback.config(
                    text=f"{guess} is too high. The number is between {self.low} and {self.high}. Try again!"
                )
            else:  # If the guess is correct
                self.feedback.config(text=f"Congratulations! {guess} is correct.")
                self.end_game()

            if self.current_mode == "Game" and self.remaining_attempts <= 0:  # If the user runs out of attempts
                self.feedback.config(text=f"Sorry, you've run out of attempts. The number was {self.number}.")
                self.end_game()

            if self.current_mode == "Game":
                self.remaining_label.config(text=f"Remaining attempts: {self.remaining_attempts}")

        except ValueError:
            self.feedback.config(text="Please enter a valid number.")  # Handle invalid input

    def end_game(self):
        """
        Ends the game and provides an option to restart or quit.
        """
        self.submit_button.config(state=tk.DISABLED)  # Disable the guess input after game ends

        # Create restart and quit buttons
        restart_button = tk.Button(
            self.game_frame, text="Restart Game", font=("Arial", 12), bg="#87ceeb", fg="white", command=self.restart_game
        )
        restart_button.pack(pady=10)

        quit_button = tk.Button(
            self.game_frame, text="Quit", font=("Arial", 12), bg="#ff6347", fg="white", command=self.quit_game
        )
        quit_button.pack(pady=10)

    def restart_game(self):
        """
        Restarts the game, resetting all necessary variables.
        """
        self.game_frame.pack_forget()  # Hide the current game frame
        self.start_game()  # Start a new game

    def quit_game(self):
        """
        Quits the game and closes the application.
        """
        self.root.quit()


# Create the Tkinter root window and pass it to the GuessingGameApp
root = tk.Tk()
game_app = GuessingGameApp(root)

root.mainloop()  # Start the Tkinter main loop


