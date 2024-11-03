import tkinter as tk
from tkinter import messagebox, ttk
from database import (
    save_user,
    save_tweet,
    get_all_tweets,
    users_collection,
    tweets_collection,
)
from models import User, Tweet


class TwitterCloneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Clone")
        self.current_user_id = None
        self.current_username = None

        # Create the main frame for login/register
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=10)

        tk.Label(self.main_frame, text="Welcome to Twitter Clone!").grid(
            row=0, columnspan=2
        )

        tk.Button(
            self.main_frame, text="Register", command=self.open_register_window
        ).grid(row=1, column=0)
        tk.Button(self.main_frame, text="Login", command=self.open_login_window).grid(
            row=1, column=1
        )

    def open_register_window(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")

        tk.Label(self.register_window, text="Username").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.register_window)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.register_window, text="Email").grid(row=1, column=0)
        self.email_entry = tk.Entry(self.register_window)
        self.email_entry.grid(row=1, column=1)

        tk.Label(self.register_window, text="Password").grid(row=2, column=0)
        self.password_entry = tk.Entry(self.register_window, show="*")
        self.password_entry.grid(row=2, column=1)

        tk.Button(
            self.register_window, text="Register", command=self.register_user
        ).grid(row=3, columnspan=2)

    def open_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")

        tk.Label(self.login_window, text="Login Username").grid(row=0, column=0)
        self.login_username_entry = tk.Entry(self.login_window)
        self.login_username_entry.grid(row=0, column=1)

        tk.Label(self.login_window, text="Password").grid(row=1, column=0)
        self.login_password_entry = tk.Entry(self.login_window, show="*")
        self.login_password_entry.grid(row=1, column=1)

        tk.Button(self.login_window, text="Login", command=self.login_user).grid(
            row=2, columnspan=2
        )

    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()  # Make sure to hash this

        if username and email and password:
            new_user = User(username=username, email=email, password=password)
            user_id = save_user(new_user)
            new_user.user_id = user_id  # Store the returned ObjectId in the User object
            messagebox.showinfo("Success", "User registered successfully!")
            self.username_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.register_window.destroy()  # Close register window
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        # Check for user in the database (you'll want to hash the password for this check)
        user = users_collection.find_one(
            {"username": username, "password": password}
        )  # Hash check needed

        if user:
            self.current_user_id = user["_id"]  # Store ObjectId of the logged-in user
            self.current_username = user["username"]  # Store the username
            messagebox.showinfo("Success", "Logged in successfully!")
            self.login_window.destroy()  # Close login window
            self.open_tweet_window()  # Open tweet window
        else:
            messagebox.showwarning("Warning", "Invalid username or password.")

    def open_tweet_window(self):
        self.tweet_window = tk.Toplevel(self.root)
        self.tweet_window.title("Tweet Window")

        tk.Button(
            self.tweet_window, text="Post Tweet", command=self.open_post_tweet_window
        ).pack(pady=10)

        # Create a Treeview for displaying tweets
        self.tweets_tree = ttk.Treeview(
            self.tweet_window,
            columns=("Content", "User", "Likes", "Retweets"),
            show="headings",
        )
        self.tweets_tree.heading("Content", text="Tweet Content")
        self.tweets_tree.heading("User", text="User")
        self.tweets_tree.heading("Likes", text="Likes")
        self.tweets_tree.heading("Retweets", text="Retweets")
        self.tweets_tree.pack(pady=10, fill="both", expand=True)

        self.load_tweets()

    def open_post_tweet_window(self):
        self.post_tweet_window = tk.Toplevel(self.tweet_window)
        self.post_tweet_window.title("Post a Tweet")

        tk.Label(self.post_tweet_window, text="Tweet Content").grid(row=0, column=0)
        self.tweet_content_entry = tk.Entry(self.post_tweet_window, width=50)
        self.tweet_content_entry.grid(row=0, column=1)

        tk.Button(self.post_tweet_window, text="Submit", command=self.post_tweet).grid(
            row=1, columnspan=2
        )

    def post_tweet(self):
        content = self.tweet_content_entry.get()
        if content and self.current_user_id:
            new_tweet = Tweet(user_id=self.current_user_id, content=content)
            save_tweet(new_tweet)
            messagebox.showinfo("Success", "Tweet posted successfully!")
            self.tweet_content_entry.delete(0, tk.END)
            self.load_tweets()
            self.post_tweet_window.destroy()  # Close the post tweet window
        else:
            messagebox.showwarning("Warning", "Please enter a tweet.")

    def load_tweets(self):
        for row in self.tweets_tree.get_children():
            self.tweets_tree.delete(row)  # Clear existing rows

        tweets = get_all_tweets()
        for tweet in tweets:
            user = users_collection.find_one({"_id": tweet["user_id"]})
            username = user["username"] if user else "Unknown User"

            like_count = len(tweet["likes"])
            retweet_count = len(tweet["retweets"])

            # Insert tweet data into the Treeview
            self.tweets_tree.insert(
                "",
                "end",
                values=(tweet["content"], username, like_count, retweet_count),
            )

        # Add an "Interact More" button for each tweet
        for tweet in tweets:
            interact_button = tk.Button(
                self.tweets_tree,
                text="Interact More",
                command=lambda t=tweet: self.open_interact_window(t),
            )
            self.tweets_tree.insert(
                "", "end", values=(interact_button,)
            )  # Add button to the Treeview

    def open_interact_window(self, tweet):
        self.interact_window = tk.Toplevel(self.tweet_window)
        self.interact_window.title("Interact with Tweet")

        tk.Label(self.interact_window, text=f"Tweet: {tweet['content']}").pack(pady=10)

        tk.Button(
            self.interact_window, text="Like", command=lambda: self.like_tweet(tweet)
        ).pack(pady=5)
        tk.Button(
            self.interact_window, text="Retweet", command=lambda: self.retweet(tweet)
        ).pack(pady=5)

        tk.Label(self.interact_window, text="Comment").pack(pady=5)
        self.comment_entry = tk.Entry(self.interact_window, width=50)
        self.comment_entry.pack(pady=5)
        tk.Button(
            self.interact_window,
            text="Submit Comment",
            command=lambda: self.comment_tweet(tweet),
        ).pack(pady=5)

    def like_tweet(self, tweet):
        if self.current_user_id not in tweet["likes"]:
            tweet["likes"].append(self.current_user_id)
            tweets_collection.update_one(
                {"_id": tweet["_id"]}, {"$set": {"likes": tweet["likes"]}}
            )
            messagebox.showinfo("Success", "Tweet liked!")
        else:
            messagebox.showwarning("Warning", "You have already liked this tweet.")
        self.load_tweets()  # Refresh the tweet list

    def retweet(self, tweet):
        if self.current_user_id not in tweet["retweets"]:
            new_tweet = Tweet(
                user_id=self.current_user_id, content=f"RT: {tweet['content']}"
            )
            save_tweet(new_tweet)
            tweet["retweets"].append(self.current_user_id)
            tweets_collection.update_one(
                {"_id": tweet["_id"]}, {"$set": {"retweets": tweet["retweets"]}}
            )
            messagebox.showinfo("Success", "Tweet retweeted!")
        else:
            messagebox.showwarning("Warning", "You have already retweeted this tweet.")
        self.load_tweets()  # Refresh the tweet list

    def comment_tweet(self, tweet):
        comment_content = self.comment_entry.get()
        if comment_content and self.current_user_id:
            comment = {"user_id": self.current_user_id, "content": comment_content}
            tweet["comments"].append(comment)
            tweets_collection.update_one(
                {"_id": tweet["_id"]}, {"$set": {"comments": tweet["comments"]}}
            )
            messagebox.showinfo("Success", "Comment added!")
            self.comment_entry.delete(0, tk.END)
            self.load_tweets()  # Refresh the tweet list
        else:
            messagebox.showwarning("Warning", "Please enter a comment.")

    def get_tweet_by_content(self, content):
        return tweets_collection.find_one({"content": content})


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterCloneApp(root)
    root.mainloop()
