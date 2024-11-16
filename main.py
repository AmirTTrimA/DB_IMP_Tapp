import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from database import (
    save_user,
    save_tweet,
    get_all_tweets,
    users_collection,
    tweets_collection,
    db,
)
from models import User, Tweet


class TwitterCloneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Clone")
        self.current_user_id = None
        self.current_username = None
        self.current_user = None
        self.db = db

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

    # ------------------ User Registration and Login ------------------
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

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        user = users_collection.find_one({"username": username, "password": password})

        if user:
            self.current_user_id = user["_id"]
            self.current_username = user["username"]
            self.current_user = user
            user["last_active"] = datetime.now()
            messagebox.showinfo("Success", "Logged in successfully!")
            self.login_window.destroy()
            self.open_tweet_window()
        else:
            messagebox.showwarning("Warning", "Invalid username or password.")

    # ------------------ Tweet Handling ------------------
    def open_tweet_window(self):
        if hasattr(self, "tweet_window") and self.tweet_window.winfo_exists():
            self.tweet_window.destroy()

        self.tweet_window = tk.Toplevel(self.root)
        self.tweet_window.title("Tweet Window")

        self.refresh_button = tk.Button(
            self.tweet_window, text="Refresh", command=self.refresh_tweets
        )
        self.refresh_button.pack(pady=10)

        tk.Button(
            self.tweet_window, text="Post Tweet", command=self.open_post_tweet_window
        ).pack(pady=10)

        tk.Button(
            self.tweet_window, text="View Profile", command=self.open_profile_window
        ).pack(pady=10)

        # Buttons for aggregations
        tk.Button(
            self.tweet_window,
            text="Most Active Users",
            command=self.show_most_active_users,
        ).pack(pady=10)

        tk.Button(
            self.tweet_window,
            text="Most Liked Tweets",
            command=self.show_most_liked_tweets,
        ).pack(pady=10)

        tk.Button(
            self.tweet_window,
            text="Most Retweeted Tweets",
            command=self.show_most_retweeted_tweets,
        ).pack(pady=10)

        tk.Button(
            self.tweet_window,
            text="User Following Ratio",
            command=self.show_user_following_ratio,
        ).pack(pady=10)

        tk.Button(
            self.tweet_window, text="Recent Tweets", command=self.show_recent_tweets
        ).pack(pady=10)

        tk.Button(
            self.tweet_window,
            text="Hashtag Usage Over Time",
            command=self.show_hashtag_usage_over_time,
        ).pack(pady=10)

        tk.Button(
            self.tweet_window,
            text="User Interaction Summary",
            command=self.show_user_interaction_summary,
        ).pack(pady=10)

        self.canvas = tk.Canvas(self.tweet_window)
        self.scrollbar = tk.Scrollbar(
            self.tweet_window, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.load_tweets()

    def refresh_tweets(self):
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
        self.mentions_dropdown["values"] = self.get_usernames()
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
                hashtags=[tag.strip() for tag in hashtags],
                mentions=mentions,
                visibility="private" if is_private else "public",
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
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        tweets = get_all_tweets()
        for tweet in tweets:
            user = users_collection.find_one({"_id": tweet["user_id"]})
            username = user["username"] if user else "Unknown User"

            # Fetch likes and retweets from the views
            like_count = self.get_like_count(tweet["_id"])
            retweet_count = self.get_retweet_count(tweet["_id"])

            tweet_label = tk.Label(
                self.scrollable_frame,
                text=f"{username}: {tweet['content']} - Likes: {like_count} - Retweets: {retweet_count}",
            )
            tweet_label.pack(anchor="w")

            see_profile_button = tk.Button(
                self.scrollable_frame,
                text="See Profile",
                command=lambda user_id=tweet["user_id"]: self.open_profile_window(
                    user_id
                ),
            )
            see_profile_button.pack(anchor="w", pady=(0, 10))

            interact_button = tk.Button(
                self.scrollable_frame,
                text="Interact More",
                command=lambda t=tweet: self.open_interact_window(t),
            )
            interact_button.pack(anchor="w", pady=(0, 10))

    def get_like_count(self, tweet_id):
        result = tweets_collection.aggregate(
            [
                {"$match": {"_id": tweet_id}},
                {"$project": {"like_count": {"$size": "$likes"}}},
            ]
        )
        return next(result, {}).get("like_count", 0)

    def get_retweet_count(self, tweet_id):
        result = tweets_collection.aggregate(
            [
                {"$match": {"_id": tweet_id}},
                {"$project": {"retweet_count": {"$size": "$retweets"}}},
            ]
        )
        return next(result, {}).get("retweet_count", 0)

    # ------------------ Aggregation Methods ------------------
    def show_most_active_users(self):
        active_users = list(self.db.most_active_users.find())
        self.display_results("Most Active Users", active_users)

    def show_most_liked_tweets(self):
        liked_tweets = list(self.db.most_liked_tweets.find())
        self.display_results("Most Liked Tweets", liked_tweets)

    def show_most_retweeted_tweets(self):
        retweeted_tweets = list(self.db.most_retweeted_tweets.find())
        self.display_results("Most Retweeted Tweets", retweeted_tweets)

    def show_user_following_ratio(self):
        following_ratios = list(self.db.user_following_ratio.find())
        self.display_results("User Following Ratio", following_ratios)

    def show_recent_tweets(self):
        recent_tweets = list(self.db.recent_tweets.find())
        self.display_results("Recent Tweets", recent_tweets)

    def show_hashtag_usage_over_time(self):
        hashtag_usage = list(self.db.hashtag_usage_over_time.find())
        self.display_results("Hashtag Usage Over Time", hashtag_usage)

    def show_user_interaction_summary(self):
        interaction_summary = list(self.db.user_interaction_summary.find())
        self.display_results("User Interaction Summary", interaction_summary)

    def display_results(self, title, results):
        results_window = tk.Toplevel(self.root)
        results_window.title(title)

        for index, result in enumerate(results):
            label = tk.Label(results_window, text=str(result))
            label.pack(anchor="w")

        if not results:
            tk.Label(results_window, text="No results found.").pack(anchor="w")

    # ------------------ Interactions with Tweets ------------------
    def open_interact_window(self, tweet):
        self.interact_window = tk.Toplevel(self.tweet_window)
        self.interact_window.title("Interact with Tweet")

        tk.Label(self.interact_window, text=f"Tweet: {tweet['content']}").pack(pady=10)

        like_count = self.get_like_count(tweet["_id"])
        retweet_count = self.get_retweet_count(tweet["_id"])

        tk.Label(self.interact_window, text=f"Likes: {like_count}").pack(pady=10)

        tk.Button(
            self.interact_window, text="Like", command=lambda: self.like_tweet(tweet)
        ).pack(pady=5)

        tk.Label(self.interact_window, text=f"Retweets: {retweet_count}").pack(pady=10)

        tk.Button(
            self.interact_window, text="Retweet", command=lambda: self.retweet(tweet)
        ).pack(pady=5)

        tk.Label(self.interact_window, text=f"Hashtags: {(tweet['hashtags'])}").pack(
            pady=10
        )

        tk.Label(
            self.interact_window, text=f"Comments: {len(tweet.get('comments', []))}"
        ).pack(pady=10)

        tk.Label(self.interact_window, text="Comments:").pack(pady=5)

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

    # ------------------ Profile Management ------------------
    def open_profile_window(self, user_id=None):
        if user_id is None:
            user_id = (
                self.current_user_id
            )  # Default to current user if no ID is provided
            editable = True  # This is the logged-in user's profile
        else:
            editable = False  # This is another user's profile

        self.profile_window = tk.Toplevel(self.root)
        self.profile_window.title("Profile")

        user = users_collection.find_one({"_id": user_id})
        if user:
            # Create labels and entry fields
            self.username_var = tk.StringVar(value=user["username"])
            self.bio_var = tk.StringVar(value=user.get("bio", "No bio available."))
            self.email_var = tk.StringVar(
                value=user.get("email", "No email available.")
            )

            tk.Label(self.profile_window, text="Username:").grid(row=0, column=0)
            self.username_entry = tk.Entry(
                self.profile_window, textvariable=self.username_var
            )
            self.username_entry.grid(row=0, column=1)
            if not editable:
                self.username_entry.config(state="readonly")

            tk.Label(self.profile_window, text="Bio:").grid(row=1, column=0)
            self.bio_entry = tk.Entry(self.profile_window, textvariable=self.bio_var)
            self.bio_entry.grid(row=1, column=1)
            if not editable:
                self.bio_entry.config(state="readonly")

            tk.Label(self.profile_window, text="Email:").grid(row=2, column=0)
            self.email_entry = tk.Entry(
                self.profile_window, textvariable=self.email_var
            )
            self.email_entry.grid(row=2, column=1)
            if not editable:
                self.email_entry.config(state="readonly")

            post_count = self.count_user_posts(user_id)
            tk.Label(self.profile_window, text="Number of Posts:").grid(row=3, column=0)
            tk.Label(self.profile_window, text=post_count).grid(row=3, column=1)

            followers_count = len(user.get("followers", []))
            following_count = len(user.get("following", []))

            tk.Button(
                self.profile_window,
                text=f"Followers ({followers_count})",
                command=lambda: self.open_followers_window(user["followers"]),
            ).grid(row=4, columnspan=2)

            tk.Button(
                self.profile_window,
                text=f"Following ({following_count})",
                command=lambda: self.open_following_window(user["following"]),
            ).grid(row=5, columnspan=2)

            if (
                user_id != self.current_user_id
            ):  # Only show follow/unfollow for other users
                follow_button = tk.Button(
                    self.profile_window,
                    text="Follow"
                    if user_id not in self.current_user.get("following", [])
                    else "Unfollow",
                    command=lambda uid=user_id: self.toggle_follow(uid),
                )
                follow_button.grid(row=6, columnspan=2)

            if editable:  # Show Edit and Save buttons for the logged-in user
                tk.Button(
                    self.profile_window, text="Edit", command=lambda: self.toggle_edit()
                ).grid(row=7, column=0)

                save_button = tk.Button(
                    self.profile_window,
                    text="Save",
                    command=lambda: self.save_profile(user_id),
                    state="disabled",  # Initially disabled
                )
                save_button.grid(row=7, column=1)

        else:
            tk.Label(self.profile_window, text="User not found.").pack(pady=10)

    def toggle_edit(self):
        # Toggle the state of the entry fields
        current_state = self.username_entry["state"]
        new_state = "normal" if current_state == "readonly" else "readonly"
        self.username_entry.config(state=new_state)
        self.bio_entry.config(state=new_state)
        self.email_entry.config(state=new_state)

        # Toggle the Save button state
        save_button = self.profile_window.grid_slaves(row=7, column=1)[
            0
        ]  # Get the Save button
        save_button.config(state="normal" if new_state == "normal" else "disabled")

    def check_existing_user_info(self, user_id, username, email):
        # Check for existing username
        existing_user = users_collection.find_one({"username": username})
        user = users_collection.find_one({"_id": user_id})
        if existing_user:
            if user["username"] == username:
                return None
            return "username"

        # Check for existing email
        existing_email = users_collection.find_one({"email": email})
        if existing_email:
            if user["email"] == email:
                return None
            return "email"

        return None  # No duplicates found

    def save_profile(self, user_id):
        # Update user information in the database
        new_username = self.username_var.get()
        new_email = self.email_var.get()
        # Check for existing username or email
        duplicate_field = self.check_existing_user_info(
            user_id, new_username, new_email
        )
        if duplicate_field:
            messagebox.showerror(
                "Error",
                f"The {duplicate_field} is already in use. Please choose another.",
            )
            return  # Exit the method if there are duplicates

        updated_user = {
            "username": self.username_var.get(),
            "bio": self.bio_var.get(),
            "email": self.email_var.get(),
        }

        users_collection.update_one({"_id": user_id}, {"$set": updated_user})
        messagebox.showinfo("Success", "Profile updated successfully.")
        self.toggle_edit()  # Disable editing after saving

    def toggle_follow(self, user_id):
        # Get the current user's following list
        following_list = self.current_user.get("following", [])
        
        if user_id in following_list:
            # Unfollow logic
            following_list.remove(user_id)
            messagebox.showinfo("Success", "Unfollowed user.")
            
            # Remove current user from the followed user's followers list
            users_collection.update_one(
                {"_id": user_id},
                {"$pull": {"followers": self.current_user_id}}  # Remove current user from followers
            )
        else:
            # Follow logic
            following_list.append(user_id)
            messagebox.showinfo("Success", "Followed user.")
            
            # Add current user to the followed user's followers list
            users_collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"followers": self.current_user_id}}  # Add current user to followers
            )

        # Update the current user in the database
        users_collection.update_one(
            {"_id": self.current_user_id},
            {"$set": {"following": following_list}}  # Update following list
        )


    def count_user_posts(self, user_id):
        return tweets_collection.count_documents({"user_id": user_id})

    # Add methods for opening followers and following windows if needed
    def open_followers_window(self, followers):
        followers_window = tk.Toplevel(self.root)
        followers_window.title("Followers")
        for follower_id in followers:
            follower = users_collection.find_one({"_id": follower_id})
            tk.Label(followers_window, text=follower["username"]).pack()

    def open_following_window(self, following):
        following_window = tk.Toplevel(self.root)
        following_window.title("Following")
        for following_id in following:
            following_user = users_collection.find_one({"_id": following_id})
            tk.Label(following_window, text=following_user["username"]).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterCloneApp(root)
    root.mainloop()
