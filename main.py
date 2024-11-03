# main.py
import tkinter as tk
from tkinter import messagebox
from database import save_user, save_tweet, get_all_tweets, users_collection
from models import User, Tweet
from bson import ObjectId

class TwitterCloneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Clone")
        self.current_user_id = None

        # User Registration Frame
        self.register_frame = tk.Frame(self.root)
        self.register_frame.pack(pady=10)

        tk.Label(self.register_frame, text="Username").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.register_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.register_frame, text="Email").grid(row=1, column=0)
        self.email_entry = tk.Entry(self.register_frame)
        self.email_entry.grid(row=1, column=1)

        tk.Label(self.register_frame, text="Password").grid(row=2, column=0)
        self.password_entry = tk.Entry(self.register_frame, show='*')
        self.password_entry.grid(row=2, column=1)

        tk.Button(self.register_frame, text="Register", command=self.register_user).grid(row=3, columnspan=2)

        # User Login Frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=10)

        tk.Label(self.login_frame, text="Login Username").grid(row=0, column=0)
        self.login_username_entry = tk.Entry(self.login_frame)
        self.login_username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password").grid(row=1, column=0)
        self.login_password_entry = tk.Entry(self.login_frame, show='*')
        self.login_password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Login", command=self.login_user).grid(row=2, columnspan=2)

        # Tweet Frame
        self.tweet_frame = tk.Frame(self.root)
        self.tweet_frame.pack(pady=10)

        tk.Label(self.tweet_frame, text="Tweet").grid(row=0, column=0)
        self.tweet_entry = tk.Entry(self.tweet_frame, width=50)
        self.tweet_entry.grid(row=0, column=1)

        tk.Button(self.tweet_frame, text="Post Tweet", command=self.post_tweet).grid(row=1, columnspan=2)

        # Display Tweets
        self.tweets_frame = tk.Frame(self.root)
        self.tweets_frame.pack(pady=10)

        self.tweets_text = tk.Text(self.tweets_frame, width=60, height=10)
        self.tweets_text.pack()

        self.load_tweets()

    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()  # Make sure to hash this

        if username and email and password:
            new_user = User(username=username, email=email, password=password)
            user_id = save_user(new_user)
            new_user.user_id = user_id
            messagebox.showinfo("Success", "User registered successfully!")
            self.username_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        # Check for user in the database (you'll want to hash the password for this check)
        user = users_collection.find_one({"username": username, "password": password})  # Hash check needed

        if user:
            self.current_user_id = user['_id']  # Store ObjectId of the logged-in user
            messagebox.showinfo("Success", "Logged in successfully!")
            self.login_username_entry.delete(0, tk.END)
            self.login_password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Invalid username or password.")

    def post_tweet(self):
        content = self.tweet_entry.get()
        if content and self.current_user_id:
            new_tweet = Tweet(user_id=self.current_user_id, content=content)
            save_tweet(new_tweet)
            messagebox.showinfo("Success", "Tweet posted successfully!")
            self.tweet_entry.delete(0, tk.END)
            self.load_tweets()
        else:
            messagebox.showwarning("Warning", "Please enter a tweet or log in.")

    def load_tweets(self):
        self.tweets_text.delete(1.0, tk.END)  # Clear existing text
        tweets = get_all_tweets()
        for tweet in tweets:
            self.tweets_text.insert(tk.END, f"{tweet['content']} (by {tweet['user_id']})\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterCloneApp(root)
    root.mainloop()
