import sqlite3
import urllib.parse
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DB_NAME = "maposh16.db"

# --- 1. DATABASE SETUP (Built-in Python SQLite) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            category TEXT NOT NULL,
            town TEXT NOT NULL,
            area TEXT,
            image_url TEXT,
            business_name TEXT NOT NULL,
            business_phone TEXT NOT NULL,
            business_whatsapp TEXT NOT NULL
        )
    """)
    
    # Add starter listings if database is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Type-C 65W Fast Charger", 1200, "Electronics", "Kapsabet", "Town Centre",
             "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=600&q=80",
             "Sam Tech & Spares", "0712345678", "254712345678"),
            ("Executive Fade & Beard Trim", 300, "Beauty & Grooming", "Kapsabet", "Kipchoge St",
             "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=600&q=80",
             "Classic Kinyozi", "0722112233", "254722112233"),
            ("Air Force 1 (Grade 1)", 2500, "Fashion", "Eldoret", "Oginga Odinga St",
             "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=600&q=80",
             "Rift Kicks Store", "0733445566", "254733445566"),
            ("Smokie Pasua with Kachumbari", 50, "Food", "Kapsabet", "Near Stage",
             "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?auto=format&fit=crop&w=600&q=80",
             "Mama Brian Snacks", "0799887766", "254799887766")
        ]
        cursor.executemany("""
            INSERT INTO products 
            (title, price, category, town, area, image_url, business_name, business_phone, business_whatsapp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()
    conn.close()

# --- 2. WHATSAPP LINK BUILDER ---
def get_whatsapp_url(phone, title, price, business_name):
    clean_digits = "".join([c for c in phone if c.isdigit()])
    if clean_digits.startswith("0"):
        clean_digits = "254" + clean_digits[1:]
    message = f"Sasa {business_name}, nimeona '{title}' kwa Maposh16 ikiwa KSh {price:,}. Bado iko available?"
    return f"https://wa.me/{clean_digits}?text={urllib.parse.quote(message)}"

app.jinja_env.filters["whatsapp_url"] = get_whatsapp_url

# --- 3. HTML/TAILWIND TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Maposh16 - Local Marketplace</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 pb-20">

  <!-- TOP HEADER -->
  <header class="bg-white border-b sticky top-0 z-30 shadow-xs">
    <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-extrabold text-lg">M</div>
        <div>
          <h1 class="font-bold text-lg leading-tight text-slate-800">Maposh<span class="text-emerald-600">16</span></h1>
          <p class="text-[10px] text-slate-400 font-medium">Local Business Finder (Python Powered)</p>
        </div>
      </div>
      <button onclick="document.getElementById('modal').classList.remove('hidden')" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3.5 py-2 rounded-lg transition">
        + Add Hustle
      </button>
    </div>

    <!-- SEARCH & FILTER FORM -->
    <form method="GET" action="/" class="max-w-4xl mx-auto px-4 pb-3 flex gap-2">
      <input type="text" name="q" value="{{ query }}" placeholder="Search charger, fade, shoes..." 
             class="flex-1 bg-slate-100 border border-slate-200 text-sm rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500">
      
      <select name="town" onchange="this.form.submit()" class="bg-slate-100 border border-slate-200 text-xs font-medium rounded-lg px-2 py-2 outline-none">
        {% for t in towns %}
          <option value="{{ t }}" {% if selected_town == t %}selected{% endif %}>{{ t }}</option>
        {% endfor %}
      </select>
      <input type="hidden" name="cat" value="{{ selected_cat }}">
      <button type="submit" class="bg-slate-800 text-white text-xs px-3 rounded-lg font-medium">Search</button>
    </form>

    <!-- CATEGORIES -->
    <div class="max-w-4xl mx-auto px-4 pb-2.5 flex gap-2 overflow-x-auto">
      {% for c in categories %}
        <a href="/?q={{ query }}&town={{ selected_town }}&cat={{ c }}"
           class="whitespace-nowrap px-3 py-1 rounded-full text-xs font-medium transition {% if selected_cat == c %}bg-slate-900 text-white{% else %}bg-slate-100 text-slate-600 hover:bg-slate-200{% endif %}">
          {{ c }}
        </a>
      {% endfor %}
    </div>
  </header>

  <!-- LISTINGS FEED -->
  <main class="max-w-4xl mx-auto px-4 mt-5">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-500">Available Deals ({{ products|length }})</h2>
      <span class="text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-medium">Verified Mtaa Sellers</span>
    </div>

    {% if products|length == 0 %}
      <div class="text-center py-16 bg-white border rounded-xl">
        <p class="text-gray-500 text-sm">Hakuna bidhaa hapa bado.</p>
        <a href="/" class="mt-2 inline-block text-emerald-600 font-semibold text-xs underline">Reset Filters</a>
      </div>
    {% else %}
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        {% for item in products %}
          <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col justify-between">
            <div>
              <img src="{{ item[6] }}" alt="{{ item[1] }}" class="w-full h-36 object-cover bg-slate-100" loading="lazy">
              <div class="p-2.5">
                <span class="text-[10px] uppercase font-bold text-slate-400">{{ item[3] }}</span>
                <h3 class="font-semibold text-xs text-slate-900 truncate mt-0.5">{{ item[1] }}</h3>
                <p class="text-sm font-extrabold text-emerald-600 mt-1">KSh {{ "{:,}".format(item[2]) }}</p>
                <p class="text-[11px] text-slate-500 mt-0.5 truncate">📍 {{ item[7] }} • {{ item[4] }}</p>
              </div>
            </div>

            <!-- ACTION BUTTONS -->
            <div class="p-2.5 pt-0 grid grid-cols-2 gap-1.5 mt-2">
              <a href="{{ item[9]|whatsapp_url(item[1], item[2], item[7]) }}" target="_blank"
                 class="bg-green-600 hover:bg-green-700 text-white rounded-md py-1.5 text-center text-[11px] font-semibold transition">
                 WhatsApp
              </a>
              <a href="tel:{{ item[8] }}"
                 class="bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-md py-1.5 text-center text-[11px] font-semibold transition">
                 Call
              </a>
            </div>
          </div>
        {% endfor %}
      </div>
    {% endif %}
  </main>

  <!-- ADD LISTING MODAL -->
  <div id="modal" class="hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div class="bg-white w-full max-w-sm rounded-2xl p-5 shadow-xl max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-sm text-slate-800">Post Item on Maposh16</h3>
        <button onclick="document.getElementById('modal').classList.add('hidden')" class="text-slate-400 hover:text-slate-600 text-lg font-bold">✕</button>
      </div>

      <form method="POST" action="/add" class="space-y-3">
        <div>
          <label class="text-[11px] font-bold text-slate-600 block mb-1">Item or Service Title</label>
          <input required type="text" name="title" placeholder="e.g. Phone Charger, Clean Fade" class="w-full text-xs border rounded-lg p-2.5 outline-none">
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">Price (KSh)</label>
            <input required type="number" name="price" placeholder="300" class="w-full text-xs border rounded-lg p-2.5 outline-none">
          </div>
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">Category</label>
            <select name="category" class="w-full text-xs border rounded-lg p-2.5 outline-none">
              <option value="Electronics">Electronics</option>
              <option value="Beauty & Grooming">Beauty & Grooming</option>
              <option value="Fashion">Fashion</option>
              <option value="Food">Food</option>
              <option value="Services">Services</option>
            </select>
          </div>
        </div>

        <div>
          <label class="text-[11px] font-bold text-slate-600 block mb-1">Business Name</label>
          <input required type="text" name="business_name" placeholder="e.g. Kip Spares" class="w-full text-xs border rounded-lg p-2.5 outline-none">
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">Town</label>
            <select name="town" class="w-full text-xs border rounded-lg p-2.5 outline-none">
              <option value="Kapsabet">Kapsabet</option>
              <option value="Eldoret">Eldoret</option>
              <option value="Nairobi">Nairobi</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">Area / Landmark</label>
            <input type="text" name="area" placeholder="e.g. Stage, CBD" class="w-full text-xs border rounded-lg p-2.5 outline-none">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">Phone Number</label>
            <input required type="text" name="phone" placeholder="0712345678" class="w-full text-xs border rounded-lg p-2.5 outline-none">
          </div>
          <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">WhatsApp No.</label>
            <input type="text" name="whatsapp" placeholder="254712345678" class="w-full text-xs border rounded-lg p-2.5 outline-none">
          </div>
        </div>

        <div>
          <label class="text-[11px] font-bold text-slate-600 block mb-1">Photo URL</label>
          <input type="url" name="image_url" placeholder="https://..." class="w-full text-xs border rounded-lg p-2.5 outline-none">
        </div>

        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-3 rounded-lg mt-2 transition">
          Publish to Maposh16
        </button>
      </form>
    </div>
  </div>

</body>
</html>
"""

# --- 4. PYTHON ROUTES ---
@app.route("/")
def home():
    query = request.args.get("q", "").strip()
    selected_town = request.args.get("town", "All")
    selected_cat = request.args.get("cat", "All")

    categories = ["All", "Electronics", "Beauty & Grooming", "Fashion", "Food", "Services"]
    towns = ["All", "Kapsabet", "Eldoret", "Nairobi"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sql = "SELECT id, title, price, category, town, area, image_url, business_name, business_phone, business_whatsapp FROM products WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR business_name LIKE ? OR area LIKE ?)"
        term = f"%{query}%"
        params.extend([term, term, term])

    if selected_town != "All":
        sql += " AND town = ?"
        params.append(selected_town)

    if selected_cat != "All":
        sql += " AND category = ?"
        params.append(selected_cat)

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    products = cursor.fetchall()
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        products=products,
        categories=categories,
        towns=towns,
        query=query,
        selected_town=selected_town,
        selected_cat=selected_cat,
    )

@app.route("/add", methods=["POST"])
def add_product():
    title = request.form.get("title")
    price = int(request.form.get("price", 0))
    category = request.form.get("category")
    town = request.form.get("town")
    area = request.form.get("area", "")
    phone = request.form.get("phone")
    whatsapp = request.form.get("whatsapp") or phone
    image_url = request.form.get("image_url") or "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80"
    business_name = request.form.get("business_name")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products 
        (title, price, category, town, area, image_url, business_name, business_phone, business_whatsapp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, price, category, town, area, image_url, business_name, phone, whatsapp))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))
init_db()

if __name__ == "__main__":
    print("Maposh16 is running live at http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=False)


if __name__ == "__main__":
    print("Maposh16 is running live at http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=False)
