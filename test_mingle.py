import requests
import time
import json

# ==========================================
# CONFIGURATION
# ==========================================
BASE_URL = "http://136.112.8.144:8080/api" # External IP VM Google


# User Data
users = {
    "Olga":   {"username": "Olga",   "email": "olga@mingle.com",   "password": "password123"},
    "Nick":   {"username": "Nick",   "email": "nick@mingle.com",   "password": "password123"},
    "Mary":   {"username": "Mary",   "email": "mary@mingle.com",   "password": "password123"},
    "Nestor": {"username": "Nestor", "email": "nestor@mingle.com", "password": "password123"}
}

# Store tokens here after login
tokens = {}
# Store post IDs to reference them later
post_ids = {}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def register(name):
    url = f"{BASE_URL}/user/register"
    res = requests.post(url, json=users[name])
    if res.status_code in [200, 201]:
        print(f"✅ {name} Registered successfully.")
    else:
        # If already exists, that's fine for testing reruns
        print(f"ℹ️  {name} Registration: {res.text}")

def login(name):
    url = f"{BASE_URL}/user/login"
    creds = {"email": users[name]["email"], "password": users[name]["password"]}
    res = requests.post(url, json=creds)
    if res.status_code == 200:
        tokens[name] = res.headers.get('auth-token') or res.json().get('auth-token')
        print(f"✅ {name} Logged in. Token received.")
    else:
        print(f"❌ {name} Login failed: {res.text}")
        exit()

def create_post(user, title, topic, body, minutes=10):
    url = f"{BASE_URL}/posts"
    headers = {"auth-token": tokens[user]}
    data = {
        "title": title,
        "topic": topic,
        "body": body,
        "expirationMinutes": minutes
    }
    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        post = res.json()
        print(f"✅ {user} posted in {topic}: '{title}' (ID: {post['_id']})")
        return post['_id']
    else:
        print(f"❌ {user} failed to post: {res.text}")
        return None

def get_posts(user, topic):
    url = f"{BASE_URL}/posts/{topic}"
    headers = {"auth-token": tokens[user]}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        posts = res.json()
        print(f"👀 {user} sees {len(posts)} posts in {topic}.")
        return posts
    return []

def interact(user, post_id, action, text=None):
    url = f"{BASE_URL}/posts/{post_id}/interact"
    headers = {"auth-token": tokens[user]}
    data = {"action": action}
    if text:
        data["text"] = text
    
    res = requests.patch(url, json=data, headers=headers)
    if res.status_code == 200:
        print(f"✅ {user} performed '{action}' on post {post_id}.")
        return True
    elif res.status_code == 403:
        print(f"🛡️ {user} action '{action}' denied (Expired/Own Post): {res.text}")
        return False
    else:
        print(f"❌ Error: {res.text}")
        return False

# ==========================================
# TEST EXECUTION (Phase D)
# ==========================================

print_header("PHASE D: TESTING APPLICATION")

# --- TC 1 & 2: Register and Login ---
print("\n--- TC 1 & 2: Register and Auth ---")
for u in users:
    register(u)
    login(u)

# --- TC 3: Unauthorized Access ---
print("\n--- TC 3: Unauthorized Access Check ---")
try:
    res = requests.post(f"{BASE_URL}/posts", json={"title": "Hack"})
    if res.status_code == 401:
        print("✅ Unauthorized call rejected (401) as expected.")
    else:
        print(f"❌ Failed: Unauthorized call got {res.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# --- TC 4, 5, 6: Posting Messages ---
print("\n--- TC 4, 5, 6: Posting in 'Tech' ---")
# Olga posts with short expiration for later tests
post_ids["Olga_Tech"] = create_post("Olga", "Olga's Tech Talk", "Tech", "AI is cool", minutes=10) 
post_ids["Nick_Tech"] = create_post("Nick", "Nick's Gadgets", "Tech", "New iPhone review", minutes=10)
post_ids["Mary_Tech"] = create_post("Mary", "Mary's Coding", "Tech", "Python vs JS", minutes=10)

# --- TC 7: Browsing ---
print("\n--- TC 7: Nick & Olga browse 'Tech' ---")
get_posts("Nick", "Tech")
get_posts("Olga", "Tech")

# --- TC 8: Likes ---
print("\n--- TC 8: Nick & Olga like Mary's post ---")
interact("Nick", post_ids["Mary_Tech"], "like")
interact("Olga", post_ids["Mary_Tech"], "like")

# --- TC 9: Likes & Dislikes ---
print("\n--- TC 9: Nestor likes Nick, Dislikes Mary ---")
interact("Nestor", post_ids["Nick_Tech"], "like")
interact("Nestor", post_ids["Mary_Tech"], "dislike")

# --- TC 10: Verify Stats ---
print("\n--- TC 10: Nick verifies stats ---")
tech_posts = get_posts("Nick", "Tech")
for p in tech_posts:
    if p['_id'] == post_ids["Mary_Tech"]:
        print(f"   -> Mary's Post: {p['likes']} Likes, {p['dislikes']} Dislikes (Expected: 2, 1)")

# --- TC 11: Own Like Restriction ---
print("\n--- TC 11: Mary tries to like her own post ---")
# Note: Your API logic must enforce this for this test to pass "Green"
interact("Mary", post_ids["Mary_Tech"], "like") 

# --- TC 12: Comments ---
print("\n--- TC 12: Nick & Olga comment on Mary's post ---")
interact("Nick", post_ids["Mary_Tech"], "comment", "Great post Mary!")
interact("Olga", post_ids["Mary_Tech"], "comment", "Totally agree.")
interact("Nick", post_ids["Mary_Tech"], "comment", "Another point...")
interact("Olga", post_ids["Mary_Tech"], "comment", "One more thing.")

# --- TC 13: Verify Comments ---
print("\n--- TC 13: Nick checks comments ---")
tech_posts = get_posts("Nick", "Tech")
for p in tech_posts:
    if p['_id'] == post_ids["Mary_Tech"]:
        print(f"   -> Mary's Post has {len(p['comments'])} comments (Expected: 4)")

# --- TC 14: Nestor Posts in Health ---
print("\n--- TC 14: Nestor posts in 'Health' (Short Expiry) ---")
# Set expiry to extremely short (0.05 mins = 3 seconds) to test expiration
post_ids["Nestor_Health"] = create_post("Nestor", "Nestor's Health Tip", "Health", "Eat apples", minutes=0.05)

# --- TC 15: Mary Browses Health ---
print("\n--- TC 15: Mary browses 'Health' ---")
get_posts("Mary", "Health")

# --- TC 16: Mary Comments ---
print("\n--- TC 16: Mary comments on Nestor's post ---")
interact("Mary", post_ids["Nestor_Health"], "comment", "Healthy advice!")

# --- TC 17: Expiration Check ---
print("\n--- TC 17: Mary tries to dislike EXPIRED post ---")
print("   (Waiting 5 seconds for post to expire...)")
time.sleep(5) 
success = interact("Mary", post_ids["Nestor_Health"], "dislike")
if not success:
    print("✅ Expiration logic worked: Action denied.")
else:
    print("❌ Failed: Action was allowed on expired post.")

# --- TC 18: Nestor checks his post ---
print("\n--- TC 18: Nestor checks his Health post ---")
health_posts = get_posts("Nestor", "Health")
# Should see 1 comment (from before expiration) and 0 dislikes (from after expiration)

# --- TC 19: Browse Sports (Empty) ---
print("\n--- TC 19: Nick browses 'Sports' (Should be empty) ---")
get_posts("Nick", "Sport")

# --- TC 20: Highest Interest ---
print("\n--- TC 20: Nestor finds most active post in Tech ---")
# This requires client-side sorting if the API doesn't support specific sorting endpoints
# Or create a specific endpoint /api/posts/active/:topic
tech_posts = get_posts("Nestor", "Tech")
if tech_posts:
    # Python-side sort to simulate "Finding"
    most_active = sorted(tech_posts, key=lambda x: x.get('likes', 0) + x.get('dislikes', 0), reverse=True)[0]
    print(f"✅ Most Active Post Identified: '{most_active['title']}' with {most_active['likes']+most_active['dislikes']} interactions.")

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)