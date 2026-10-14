#!/bin/bash
TARGET=$1

if [ -z "$TARGET" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  AHMZ Store Database Switcher"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Usage: ./use_db.sh <niche_name>"
    echo ""
    echo "Available choices:"
    echo "  • clothing     (পাঞ্জাবি, শাড়ি, কুর্তি, পোলো)"
    echo "  • shoes        (লেদার লোফার, অক্সফোর্ড, স্নিকার্স)"
    echo "  • watches      (মেটালিক ক্রোনোগ্রাফ, অটোমেটিক, স্মার্টওয়াচ)"
    echo "  • cosmetics    (সিরাম, লিপস্টিক, প্রিমিয়াম পারফিউম)"
    echo "  • electronics  (ইয়ারবাডস, পাওয়ার ব্যাংক, চার্জিং ডক)"
    echo "  • mega_all     (সব পণ্য একসাথে - দারাজ/আড়ং স্টাইল)"
    echo ""
    echo "Example:"
    echo "  ./use_db.sh watches"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

SOURCE="db_${TARGET}.sqlite3"

if [ ! -f "$SOURCE" ]; then
    echo "❌ ফাইল পাওয়া যায়নি: '$SOURCE'"
    echo "সঠিক নাম লিখুন: clothing, shoes, watches, cosmetics, electronics, mega_all"
    exit 1
fi

cp "$SOURCE" db.sqlite3
echo "✅ সফলভাবে '$SOURCE' ডাটাবেজ সক্রিয় করা হয়েছে (db.sqlite3 হিসেবে)!"
echo "🌐 ব্রাউজারে http://127.0.0.1:8000/ রিলোড করে নতুন শপটি দেখুন।"
