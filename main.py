from flask import Flask, render_template
import datetime as dt
import requests
import re

app = Flask(__name__)

MY_NAME = 'Gavin "Siris" Martin'  # Defined globally for reuse in routes and/or functions

@app.context_processor
def inject_globals():
    return {
        'CURRENT_YEAR': dt.datetime.now().year,
        'MY_NAME': MY_NAME
    }

def slugify(title):
    return re.sub(r'\W+', '-', title.lower()).strip('-')

app.jinja_env.filters['slugify'] = slugify

def fetch_posts():
    static_posts = [
        {"title": "Man must explore, and this is exploration at its greatest",
         "subtitle": "Problems look mighty small from 150 miles up",
         "author": "Start Bootstrap",
         "date": "2023-09-24",
         "image": "explore.jpg"},
        {"title": "I believe every human has a finite number of heartbeats. I don't intend to waste any of mine.",
         "author": "Start Bootstrap",
         "date": "2023-09-18",
         "image": "heart2.jpg"},
        {"title": "Science has not yet mastered prophecy",
         "subtitle": "We predict too much for the next year and yet far too little for the next ten.",
         "author": "Start Bootstrap",
         "date": "2023-08-24",
         "image": "science.jpg"},
        {"title": "Failure is not an option",
         "subtitle": "Many say exploration is part of our destiny, but it’s actually our duty to future generations.",
         "author": "Start Bootstrap",
         "date": "2023-07-08",
         "image": "failure.jpg"}
    ]
    try:
        blog_url = "https://api.npoint.io/e52811763db21dfef489"
        blog_response = requests.get(blog_url)
        blog_response.raise_for_status()
        api_posts = blog_response.json()
        for post in api_posts:
            date_str = post.get('date', '')
            if 'T' in date_str:
                formatted_date = dt.datetime.strptime(date_str.split('T')[0], "%Y-%m-%d").strftime("%b %d, %Y %I:%M%p")
            else:
                formatted_date = dt.datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y %I:%M%p")
            post['date'] = formatted_date[:-2] + formatted_date[-2:].lower()
            post['author'] = post.get('author', 'Dr. Angela Yu')
            # Default image selection based on title keywords
            post['image'] = 'default.jpg'
            if 'explore' in post['title'].lower():
                post['image'] = 'explore.jpg'
            elif 'heart' in post['title'].lower():
                post['image'] = 'heart2.jpg'
            elif 'science' in post['title'].lower():
                post['image'] = 'science.jpg'
            elif 'failure' in post['title'].lower():
                post['image'] = 'failure.jpg'
    except requests.RequestException as e:
        print(f"Failed to retrieve blog data: {e}")
        api_posts = []
    return static_posts + api_posts

@app.route('/')
@app.route('/home')
def home():
    all_posts = fetch_posts()
    all_posts.sort(key=lambda x: x['date'], reverse=True)
    return render_template("index.html", posts=all_posts)

@app.route('/post/<slug>')
def post(slug):
    all_posts = fetch_posts()
    post = next((p for p in all_posts if slugify(p['title']) == slug), None)
    if post:
        background_image = post.get('image', 'default.jpg')
        return render_template('post.html', post=post, background_image=background_image)
    else:
        return render_template('404.html'), 404

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)
