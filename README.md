# AHMZ Artisan Lifestyle & Clothing (বাংলাদেশি ই-কমার্স প্ল্যাটফর্ম)

A complete, production-grade, and lightweight **Bangladeshi Fashion Brand E-Commerce Platform** built with **Django** and a custom **Bangladeshi styling frontend (Tailwind CSS CDN + FontAwesome 6)**, complete with a comprehensive **Store Management Dashboard Panel**.

---

## 🌟 Key Features

### 🛍️ 1. Customer Storefront (Lightweight Bangladeshi Aesthetics)
- **Authentic Bengali & English Bilingual Toggle**:
  - One-click switcher (`বাংলা` / `English`) directly in the announcement bar, header, and mobile menu.
  - Automatically switches banner announcements, navigation, badges, cart buttons, and checkout labels.
  - Categories: পাঞ্জাবি ও কাবলি (Panjabi & Kabli), ঐতিহ্যবাহী জামদানি ও সিল্ক শাড়ি (Jamdani Saree), ডিজাইনার কুর্তি ও সালোয়ার (Salwar & Kurti), ক্যাজুয়াল পোলো ও টি-শার্ট (Polo & T-shirts).
  - Currency: Bangladeshi Taka (`৳` BDT).
  - Eid Special & Festive Drop badges (✨ ঈদ কালেকশন ২০২৬ / Eid Collection 2026).
  - Bengali micro-copy & Bangladeshi context (ঢাকা ডেলিভারি ২৪-৪৮ ঘণ্টা, সারা দেশে ক্যাশ অন ডেলিভারি, ৭ দিনের সাইজ এক্সচেঞ্জ).
- **Product Catalog & Filters**:
  - Filter by Category, Gender (Men, Women, Kids, Unisex), Price range (৳500 - ৳10,000), Sort by Newest, Price, and Ratings.
  - Live search by product name, SKU, or fabric.
- **Product Details Page**:
  - High-res image gallery with alternate hover switch.
  - Interactive Size Selector (`38, 40, 42, 44, 46` for Panjabi / `S, M, L, XL, XXL`).
  - **Bangladeshi Panjabi/Dress Size Chart Modal** (Chest, Length, Sleeve, Collar in inches).
  - Instant **"হোয়াটসঅ্যাপে সরাসরি অর্ডার করুন" (Direct WhatsApp Order)** with prefilled product message.
  - Customer ratings and review submission form.
- **Shopping Bag & Cart Drawer**:
  - Session-based blazing-fast cart.
  - Quantity increment/decrement, remove items.
  - Promo code system with live discount deduction (Try code: `EID2026` or `AHMZ15`).
- **Bangladeshi Checkout**:
  - Divisions & Districts selector (Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, etc.).
  - **Delivery Area toggle with real-time recalculation**:
    - Inside Dhaka (ঢাকা সিটি): **৳৬০** (24-48 hrs).
    - Outside Dhaka (ঢাকার বাইরে সারা বাংলাদেশ): **৳১২০** (2-3 days).
  - **Payment Options**:
    - Cash on Delivery (ক্যাশ অন ডেলিভারি)
    - bKash (বিকাশ Send Money / Merchant) with Sender Number & TrxID input
    - Nagad (নগদ) with TrxID input
    - Rocket
- **Invoice & Order Confirmation**:
  - Order success memo with unique order number (e.g. `AHMZ-54210`).
  - One-click print receipt feature.
- **Live Order Tracking**:
  - Track orders by **Order Number** and **Phone Number**.
  - **5-Stage Visual Progress Stepper**: Order Placed ➔ Confirmed (Call) ➔ Processing/Packaging ➔ Handed to Courier (Steadfast/Pathao) ➔ Delivered.

---

### 📊 2. Store Manager Dashboard Panel (`/dashboard/`)
- Accessible via `/dashboard/` or header button.
- **Executive Analytics**:
  - Total Revenue (৳), Total Orders, Pending Orders counter, Active Products, Low-Stock Warning.
  - Pipeline status counters (Pending, Confirmed, Processing, Shipped, Delivered, Cancelled).
- **Order Management (`/dashboard/orders/`)**:
  - Filter by status and payment gateway (bKash / Nagad / COD).
  - Search by Order ID, Customer Name, Phone, or TrxID.
  - Update status and courier tracking consignment ID (e.g., Steadfast / Pathao).
  - Direct WhatsApp button to message customer.
  - Printable official cash memo invoice (`/dashboard/orders/<id>/invoice/`).
- **Product & Inventory Management (`/dashboard/products/`)**:
  - Add, edit, or delete clothing items.
  - Manage stock count, fabric composition, sizes, regular & discount prices.
  - Low-stock indicator badges (< 5 items).
- **Category & Coupon Management**:
  - Manage product categories.
  - Create promo codes with percentage discounts and minimum order requirements.

---

## 🚀 How to Run the Project

### 1. Activate the Virtual Environment
```bash
source venv/bin/activate
```

### 2. Run Database Migrations & Seed Data (Already Prepared)
```bash
python manage.py migrate
python seed_data.py
```

### 3. Run the Development Server
```bash
python manage.py runserver
```

Open your browser at:
- **Online Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Dashboard Panel**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔑 Admin / Manager Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 🎟️ Active Demo Promo Codes
- `EID2026`: 10% discount (Minimum order ৳1,500)
- `AHMZ15`: 15% discount (Minimum order ৳3,000)

## 📦 Test Order Tracking
- Order Number: `AHMZ-54210` | Phone: `01711223344`
- Order Number: `AHMZ-68341` | Phone: `01819887766`
- Order Number: `AHMZ-79105` | Phone: `01912334455`
