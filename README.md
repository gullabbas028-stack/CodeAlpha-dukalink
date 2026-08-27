# DukaLink — Full-Stack E-Commerce Website (Django)

DukaLink is a complete, working e-commerce web application: browse products,
view product details, add to cart, adjust quantities, check out, and place a
real order — backed by Django, Django ORM, and SQLite.

---

## 1. Project overview

DukaLink is a demo online store (Pakistani-market styled, PKR pricing) built
for a Full Stack Development internship-style project. It implements the
complete shopping workflow end to end, is mobile-responsive, and ships with
~47 seeded products across 8 categories so every feature (search, filters,
sorting, cart, checkout, orders) can be tested immediately without manual
data entry.

## 2. Features

- **Home page** — hero banner, category cards, featured / new arrivals /
  popular / on-sale sections, customer benefit strip
- **Product listing** — sidebar filters (category, price range, availability,
  rating) + sorting (newest, popular, price low→high, price high→low) + live
  result count
- **Search** — by product name, description, or category, with a friendly
  "no results" state
- **Product details page** — image, price/discount, rating, description,
  feature list, quantity selector, Add to Cart, Buy Now, related products
- **Wishlist** — heart-toggle on any product card (requires login), full
  wishlist page
- **Shopping cart** — session-based (works for guests and logged-in users),
  AJAX add/update/remove with no page reloads, live-updating totals, cart
  badge in the header
- **Checkout** — shipping details form + Cash on Delivery / demo card payment
  selection, live order summary
- **Order processing** — creates a real `Order` + `OrderItem` rows in the
  database, decrements stock, clears the cart, and redirects to a
  confirmation page with an order number (e.g. `DL-91326`)
- **User accounts** — register / login / logout, profile page with order
  history
- **Django Admin** — manage categories, products (stock/price editable
  inline), orders (with order-item inlines and status dropdown), and
  wishlist entries
- **Responsive design** — down to mobile, with a hamburger menu, 2-column
  mobile product grid, and no horizontal scrolling

## 3. Technology stack

- **Backend:** Python, Django 5, Django ORM, SQLite (dev)
- **Frontend:** HTML5, CSS3 (hand-written, no Bootstrap), vanilla JavaScript
  (fetch-based AJAX), Google Fonts (Poppins + Inter)
- **Images:** placeholder images generated per-product via placehold.co,
  color-coded by category — swappable for real photos via Django Admin
  (`Product.image` field) at any time

## 4. Project structure

```
dukalink/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                  # created after migrate
│
├── config/                     # project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── shop/                       # the e-commerce app
│   ├── models.py                # Category, Product, Order, OrderItem, Wishlist
│   ├── views.py                 # all page + AJAX endpoint views
│   ├── urls.py
│   ├── forms.py                 # CheckoutForm, RegisterForm
│   ├── admin.py
│   ├── cart.py                  # session-based cart class
│   ├── context_processors.py     # cart/wishlist counts, categories, currency
│   ├── templatetags/shop_extras.py   # {{ value|pkr }} currency filter
│   └── management/commands/seed_products.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── products.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── order_success.html
│   ├── wishlist.html
│   ├── profile.html
│   ├── partials/product_card.html
│   └── registration/{login,register}.html
│
└── static/
    ├── css/style.css
    └── js/main.js
```

## 5. Installation

```bash
# 1. Clone / unzip the project, then enter it
cd dukalink

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 6. Database setup

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates `db.sqlite3` with all tables (Category, Product, Order,
OrderItem, Wishlist, plus Django's built-in auth/session tables).

## 7. Seed demo data

```bash
python manage.py seed_products
```

This creates 8 categories and ~47 realistic products with PKR pricing,
discounts, stock levels, and ratings — enough to fully exercise search,
filtering, sorting, cart, and checkout. Run it again any time; it skips
products that already exist by name. Use `--flush` to wipe and reseed from
scratch:

```bash
python manage.py seed_products --flush
```

## 8. Create an admin user

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

## 9. Run the server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the storefront and
**http://127.0.0.1:8000/admin/** for the admin panel.

## 10. Demo credentials

No demo credentials are pre-created in the codebase (for security, only
`createsuperuser` above creates real accounts). Register a normal shopper
account from the site's **Create Account** page to test wishlist, checkout,
and order history as a logged-in user — or check out as a guest, since login
is not required to purchase.

## 11. Complete order flow (how it works)

```
Home → Shop → Product detail → Add to Cart
  → Cart updates instantly (AJAX, no reload)
  → Open Cart → change quantity → totals update live
  → Proceed to Checkout
  → Enter shipping details → choose Cash on Delivery
  → Place Order
      → Django validates stock, creates Order + OrderItem rows,
        decrements Product.stock, clears the session cart
  → Redirected to Order Confirmation page (order number shown)
  → Order appears immediately in Django Admin → Orders,
    with its items and an editable status dropdown
```

This flow was tested end-to-end (via automated HTTP requests against a
running server) before delivery, including: search, category/price/rating
filters, sorting, add/update/remove cart, guest checkout, registered-user
checkout, wishlist add/remove, login, and POST-based logout.

## 12. Django Admin capabilities

Logged in as a superuser, you can:
- Add / edit / delete products and categories (with inline price & stock
  editing directly in the list view)
- Upload real product photos (replaces the placeholder image automatically)
- View orders with full customer details and line items
- Update order status (Pending → Confirmed → Processing → Shipped →
  Delivered / Cancelled)
- View wishlist entries per user

## 13. Testing checklist

- [x] Homepage renders (hero, categories, featured/new/popular/sale rows)
- [x] Product listing renders for all 8 categories
- [x] Product detail page renders for products in every category
- [x] Search returns filtered results and an empty-state message when none match
- [x] Category, price range, availability, and rating filters all apply correctly
- [x] Sorting (newest / popular / price asc / price desc) works
- [x] Add to cart updates the header badge without a page reload
- [x] Cart quantity +/- and remove update line totals and order summary live
- [x] Checkout blocks with an empty cart (redirects back to shop)
- [x] Checkout creates an Order + OrderItem rows and decrements stock
- [x] Order confirmation page shows the correct order number and summary
- [x] Order is visible and editable in Django Admin
- [x] Wishlist requires login, and add/remove toggling works
- [x] Registration creates a working account and logs the user in
- [x] Login / POST-based logout both work correctly
- [x] Mobile responsive layout (hamburger nav, 2-column product grid, no
      horizontal scroll) down to small phone widths

## 14. Notes on scope & future improvements

This is a demo/internship-scale project, so a few things are intentionally
simple:

- **Payment** is Cash on Delivery by default; "Demo Card Payment" is clearly
  marked as a non-real, non-processing option — no card details are ever
  collected or stored.
- **Images** are auto-generated color placeholders per category; swap in
  real photos any time via the admin's `image` upload field.
- **SQLite** is used for development. `config/settings.py` isolates the
  `DATABASES` dict so swapping in PostgreSQL later is a small, contained
  change (point it at `DATABASE_URL` with `psycopg2`/`dj-database-url`).
- **Coupons/discount codes** are not implemented — `Cart.discount` is a
  placeholder property ready for that logic.

Natural next steps: PostgreSQL in production, real payment gateway
integration (clearly separated from the COD flow), coupon codes, product
reviews, and email order-confirmation notifications.
