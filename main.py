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
        password = self.password_entry.get()

        if username and email and password:
            new_user = User(username=username, email=email, password=password)
            user_id = save_user(new_user)
            new_user.user_id = user_id
            messagebox.showinfo("Success", "User registered successfully!")
            self.username_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.register_window.destroy()
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        user = users_collection.find_one({"username": username, "password": password})

        if user:
            self.current_user_id = user["_id"]
            self.current_username = user["username"]
            messagebox.showinfo("Success", "Logged in successfully!")
            self.login_window.destroy()
            self.open_tweet_window()
        else:
            messagebox.showwarning("Warning", "Invalid username or password.")

    def open_tweet_window(self):
        # Close the existing tweet window if it exists
        if hasattr(self, 'tweet_window') and self.tweet_window.winfo_exists():
            self.tweet_window.destroy()

        self.tweet_window = tk.Toplevel(self.root)
        self.tweet_window.title("Tweet Window")

        # Create the Refresh Button
        self.refresh_button = tk.Button(
            self.tweet_window, text="Refresh", command=self.open_tweet_window
        )
        self.refresh_button.pack(pady=10)

        # Create the Post Tweet Button
        tk.Button(
            self.tweet_window, text="Post Tweet", command=self.open_post_tweet_window
        ).pack(pady=10)

        # Frame for displaying tweets
        self.tweets_frame = tk.Frame(self.tweet_window)
        self.tweets_frame.pack(pady=10)

        # Load tweets initially
        self.load_tweets()

    def refresh_tweets(self):
        """Reloads the tweets by reopening the tweet window."""
        self.open_tweet_window()

    def open_post_tweet_window(self):
        self.post_tweet_window = tk.Toplevel(self.tweet_window)
        self.post_tweet_window.title("Post a Tweet")

        tk.Label(self.post_tweet_window, text="Tweet Content").grid(row=0, column=0)
        self.tweet_content_entry = tk.Entry(self.post_tweet_window, width=50)
        self.tweet_content_entry.grid(row=0, column=1)

        tk.Label(self.post_tweet_window, text="Hashtags (comma separated)").grid(
            row=1, column=0
        )
        self.hashtags_entry = tk.Entry(self.post_tweet_window, width=50)
        self.hashtags_entry.grid(row=1, column=1)

        tk.Label(self.post_tweet_window, text="Mentions").grid(row=2, column=0)
        self.mentions_var = tk.StringVar()
        self.mentions_dropdown = ttk.Combobox(
            self.post_tweet_window, textvariable=self.mentions_var
        )
        self.mentions_dropdown["values"] = (
            self.get_usernames()
        )  # Populate with usernames
        self.mentions_dropdown.grid(row=2, column=1)

        self.private_var = tk.BooleanVar()
        self.private_checkbox = tk.Checkbutton(
            self.post_tweet_window, text="Private Post", variable=self.private_var
        )
        self.private_checkbox.grid(row=3, columnspan=2)

        tk.Button(self.post_tweet_window, text="Submit", command=self.post_tweet).grid(
            row=4, columnspan=2
        )

    def get_usernames(self):
        # Fetch all usernames from the database
        users = users_collection.find()
        return [user["username"] for user in users]

    def post_tweet(self):
        content = self.tweet_content_entry.get()
        hashtags = (
            self.hashtags_entry.get().split(",") if self.hashtags_entry.get() else []
        )
        mentions = self.mentions_var.get()
        is_private = self.private_var.get()

        if content and self.current_user_id:
            new_tweet = Tweet(
                user_id=self.current_user_id,
                content=content,
                hashtags=[tag.strip() for tag in hashtags],  # Clean up whitespace
                mentions=mentions,
                visibility="private"
                if is_private
                else "public",  # Set visibility based on checkbox
            )
            save_tweet(new_tweet)
            messagebox.showinfo("Success", "Tweet posted successfully!")
            self.tweet_content_entry.delete(0, tk.END)
            self.hashtags_entry.delete(0, tk.END)
            self.mentions_var.set("")
            self.load_tweets()
            self.post_tweet_window.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter a tweet.")

    def load_tweets(self):
        # Clear the tweets_frame
        for widget in self.tweets_frame.winfo_children():
            widget.destroy()

        tweets = get_all_tweets()
        for tweet in tweets:
            user = users_collection.find_one({"_id": tweet["user_id"]})
            username = user["username"] if user else "Unknown User"

            like_count = len(tweet["likes"])
            retweet_count = len(tweet["retweets"])

            tweet_label = tk.Label(
                self.tweets_frame,
                text=f"{username}: {tweet['content']} - Likes: {like_count} - Retweets: {retweet_count}",
            )
            tweet_label.pack(anchor="w")

            interact_button = tk.Button(
                self.tweets_frame,
                text="Interact More",
                command=lambda t=tweet: self.open_interact_window(t),
            )
            interact_button.pack(
                anchor="w", pady=(0, 10)
            )  # Add some space after each button

    def refresh_tweets(self):
        self.load_tweets()

    def open_interact_window(self, tweet):
        self.interact_window = tk.Toplevel(self.tweet_window)
        self.interact_window.title("Interact with Tweet")

        tk.Label(self.interact_window, text=f"Tweet: {tweet['content']}").pack(pady=10)

        tk.Label(self.interact_window, text=f"Likes: {len(tweet['likes'])}").pack(
            pady=10
        )

        tk.Button(
            self.interact_window, text="Like", command=lambda: self.like_tweet(tweet)
        ).pack(pady=5)

        tk.Label(self.interact_window, text=f"Retweets: {len(tweet['retweets'])}").pack(
            pady=10
        )

        tk.Button(
            self.interact_window, text="Retweet", command=lambda: self.retweet(tweet)
        ).pack(pady=5)

        tk.Label(self.interact_window, text=f"Hashtags: {(tweet['hashtags'])}").pack(
            pady=10
        )

        tk.Label(self.interact_window, text=f"Comments: {len(tweet['comments'])}").pack(
            pady=10
        )

        tk.Label(self.interact_window, text="Comments:").pack(pady=5)

        # Display comments
        self.comment_listbox = tk.Listbox(self.interact_window, width=50, height=10)
        self.comment_listbox.pack(pady=5)
        self.load_comments(tweet)

        tk.Label(self.interact_window, text="Add Comment:").pack(pady=5)
        self.comment_entry = tk.Entry(self.interact_window, width=50)
        self.comment_entry.pack(pady=5)
        tk.Button(
            self.interact_window,
            text="Submit Comment",
            command=lambda: self.comment_tweet(tweet),
        ).pack(pady=5)

    def load_comments(self, tweet):
        self.comment_listbox.delete(0, tk.END)
        for comment in tweet.get("comments", []):
            user = users_collection.find_one({"_id": comment["user_id"]})
            username = user["username"] if user else "Unknown User"
            self.comment_listbox.insert(tk.END, f"{username}: {comment['content']}")

    def like_tweet(self, tweet):
        if self.current_user_id not in tweet["likes"]:
            tweet["likes"].append(self.current_user_id)
            tweets_collection.update_one(
                {"_id": tweet["_id"]}, {"$set": {"likes": tweet["likes"]}}
            )
            messagebox.showinfo("Success", "Tweet liked!")
        else:
            messagebox.showwarning("Warning", "You have already liked this tweet.")
        self.load_tweets()

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
        self.load_tweets()

    def comment_tweet(self, tweet):
        comment_content = self.comment_entry.get()
        if comment_content and self.current_user_id:
            comment = {"user_id": self.current_user_id, "content": comment_content}
            tweet.setdefault("comments", []).append(comment)
            tweets_collection.update_one(
                {"_id": tweet["_id"]}, {"$set": {"comments": tweet["comments"]}}
            )
            messagebox.showinfo("Success", "Comment added!")
            self.comment_entry.delete(0, tk.END)
            self.load_comments(tweet)
        else:
            messagebox.showwarning("Warning", "Please enter a comment.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterCloneApp(root)
    root.mainloop()
