"""Seed script for the Restaurant API.

Populates the database with coherent demo data:
- 4 categories
- 4 promo codes
- 20 restaurant tables
- 20 customers (with loyalty + preferences)
- 20 menu items (with option groups)
- 90 orders (6/day over the last 15 days, today included)
- 60 reservations (past, today and upcoming)

Run from the backend directory:
    .venv/bin/python -m src.seed [--fresh]
"""

import json
import sys
from datetime import datetime, date, time, timedelta

from sqlmodel import Session, select, SQLModel

from .core.database import engine
from .core.config import get_settings
from .models import (
    Category,
    Customer,
    CustomerLoyalty,
    CustomerPreferences,
    MenuItem,
    MenuOption,
    MenuOptionGroup,
    PromoCode,
    RestaurantTable,
    Reservation,
    Order,
    OrderItem,
)
from .enums import (
    ORDERSTATUS,
    TABLESTATUS,
    RESERVATIONSTATUS,
    PAYMENTSTATUS,
    PAYMENTMETHOD,
)

CUSTOMER_IMAGES = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1504257432389-52343af06ae3?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&auto=format&fit=crop&q=80",
]

# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"id": "cat-entrees", "name": "Entrées", "description": "Pour commencer le repas"},
    {"id": "cat-plats", "name": "Plats", "description": "Nos plats signatures"},
    {"id": "cat-desserts", "name": "Desserts", "description": "Douceurs maison"},
    {"id": "cat-boissons", "name": "Boissons", "description": "Rafraîchissements et vins"},
]

TABLE_PLACES = [
    "Intérieur", "Intérieur", "Intérieur", "Intérieur", "Intérieur",
    "Intérieur", "Intérieur", "VIP", "Intérieur", "VIP",
    "Terrasse", "Terrasse", "Terrasse", "Terrasse", "Terrasse",
    "Véranda", "Véranda", "Véranda", "Véranda", "VIP",
]

TABLE_CAPACITIES = [2, 2, 4, 4, 4, 6, 6, 8, 2, 10, 2, 2, 4, 4, 6, 2, 4, 4, 6, 12]

PROMO_CODES = [
    {
        "id": "promo-welcome",
        "code": "WELCOME10",
        "description": "Réduction de bienvenue",
        "discountType": "PERCENTAGE",
        "discountValue": 10,
        "minOrderAmount": 20,
        "requiredLoyaltyTier": None,
        "isActive": True,
    },
    {
        "id": "promo-gold",
        "code": "GOLDVIP20",
        "description": "Offre spéciale membres Gold",
        "discountType": "PERCENTAGE",
        "discountValue": 20,
        "minOrderAmount": 50,
        "requiredLoyaltyTier": "GOLD",
        "isActive": True,
    },
    {
        "id": "promo-chef",
        "code": "CHEF5EUR",
        "description": "Remise fixe du Chef",
        "discountType": "FIXED_AMOUNT",
        "discountValue": 5,
        "minOrderAmount": 30,
        "requiredLoyaltyTier": None,
        "isActive": True,
    },
    {
        "id": "promo-vip",
        "code": "VIPEXCLUSIF",
        "description": "Offre privilège VIP",
        "discountType": "PERCENTAGE",
        "discountValue": 25,
        "minOrderAmount": 40,
        "requiredLoyaltyTier": "VIP",
        "isActive": True,
    },
]

CUSTOMERS = [
    # id, firstName, lastName, email, phone, status, points, tier, discount, prefs
    ("cust-001", "Jean", "Dupont", "jean.dupont@email.com", "+33 6 12 34 56 78", "REGULAR", 120, "BRONZE", None, {"isVegetarian": True, "preferredTableNotes": "Près de la fenêtre"}),
    ("cust-002", "Sophie", "Martin", "sophie.martin@email.com", "+33 6 98 76 54 32", "VIP", 1450, "VIP", 10, {"isGlutenFree": True, "allergies": ["Arachides"]}),
    ("cust-003", "Thomas", "Bernard", "thomas.bernard@email.com", "+33 7 45 67 89 01", "BLOCKED", 0, "BRONZE", None, {}),
    ("cust-004", "Élodie", "Petit", "elodie.petit@email.com", "+33 6 22 33 44 55", "REGULAR", 450, "SILVER", None, {"preferredTableNotes": "Terrasse uniquement"}),
    ("cust-005", "Marc", "Moreau", "marc.moreau@email.com", "+33 6 33 44 55 66", "REGULAR", 890, "GOLD", None, {"isVegetarian": True, "isGlutenFree": True, "allergies": ["Lactose"]}),
    ("cust-006", "Camille", "Roux", "camille.roux@email.com", "+33 7 11 22 33 44", "REGULAR", 50, "BRONZE", None, {}),
    ("cust-007", "Lucas", "David", "lucas.david@email.com", "+33 6 55 66 77 88", "VIP", 2100, "VIP", 15, {"preferredTableNotes": "Chaise haute pour enfant requise"}),
    ("cust-008", "Léa", "Bertrand", "lea.bertrand@email.com", "+33 6 77 88 99 00", "REGULAR", 310, "SILVER", None, {"allergies": ["Fruits de mer"]}),
    ("cust-009", "Antoine", "Guerin", "antoine.guerin@email.com", "+33 7 88 99 00 11", "REGULAR", 0, "BRONZE", None, {}),
    ("cust-0010", "Julie", "Boyer", "julie.boyer@email.com", "+33 6 44 55 66 77", "REGULAR", 620, "GOLD", None, {"isVegetarian": True}),
    ("cust-011", "Hugo", "Fontaine", "hugo.fontaine@email.com", "+33 7 33 22 11 00", "REGULAR", 180, "BRONZE", None, {"preferredTableNotes": "Au calme, coin discret"}),
    ("cust-012", "Chloé", "Chevalier", "chloe.chevalier@email.com", "+33 6 99 00 11 22", "VIP", 1750, "VIP", 10, {"isGlutenFree": True}),
    ("cust-013", "Mathieu", "Girard", "mathieu.girard@email.com", "+33 6 11 33 55 77", "REGULAR", 95, "BRONZE", None, {}),
    ("cust-014", "Pauline", "Lambert", "pauline.lambert@email.com", "+33 7 66 55 44 33", "BLOCKED", 20, "BRONZE", None, {}),
    ("cust-015", "Alexandre", "Bonnet", "alex.bonnet@email.com", "+33 6 88 77 66 55", "REGULAR", 510, "SILVER", None, {"allergies": ["Soja", "Lactose"]}),
    ("cust-016", "Manon", "Francois", "manon.francois@email.com", "+33 7 22 44 66 88", "REGULAR", 740, "GOLD", None, {"isVegetarian": True, "preferredTableNotes": "Table banquet si possible"}),
    ("cust-017", "Nicolas", "Martinez", "nicolas.martinez@email.com", "+33 6 33 22 11 44", "REGULAR", 260, "SILVER", None, {}),
    ("cust-018", "Sarah", "Legrand", "sarah.legrand@email.com", "+33 7 99 88 77 66", "VIP", 3200, "VIP", 20, {"preferredTableNotes": "Client habitué table 12"}),
    ("cust-019", "Maxime", "Gautier", "maxime.gautier@email.com", "+33 6 44 33 22 11", "REGULAR", 40, "BRONZE", None, {}),
    ("cust-020", "Inès", "Perrin", "ines.perrin@email.com", "+33 7 55 44 33 22", "REGULAR", 390, "SILVER", None, {"isGlutenFree": True, "allergies": ["Coque"]}),
]

MENU_ITEMS = [
    # id, categoryId, name, description, price, status, veg, gf, prepTime, images
    ("item-1", "cat-entrees", "Salade César Poulet", "Laitue romaine, blanc de poulet grillé, parmesan, croûtons et sauce César maison.", 12.5, "AVAILABLE", False, False, 10, ["https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80"]),
    ("item-2", "cat-entrees", "Velouté de Potimarron", "Soupe onctueuse au potimarron, graines de courge torréfiées et crème fraîche.", 8.0, "AVAILABLE", True, True, 8, ["https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80"]),
    ("item-3", "cat-entrees", "Carpaccio de Bœuf", "Fines tranches de bœuf, huile d'olive au basilic, câpres et copeaux de parmesan.", 14.0, "AVAILABLE", False, True, 10, ["https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80"]),
    ("item-4", "cat-entrees", "Tartine d'Avocat & Œuf Poché", "Pain au levain, guacamole maison, œuf bio poché et graines de sésame.", 10.5, "OUT_OF_STOCK", True, False, 12, ["https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80"]),
    ("item-5", "cat-plats", "Cheeseburger Gourmet", "Steak haché pur bœuf 180g, cheddar affiné, oignons confits, bacon croustillant.", 16.5, "AVAILABLE", False, False, 15, ["https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80"]),
    ("item-6", "cat-plats", "Veggie Burger", "Galette de haricots rouges et quinoa, avocat, tomate, sauce yaourt aux herbes.", 15.0, "AVAILABLE", True, False, 15, ["https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80"]),
    ("item-7", "cat-plats", "Pavé de Saumon Rôti", "Saumon de Norvège, mousseline de patate douce et légumes de saison poêlés.", 19.5, "AVAILABLE", False, True, 20, ["https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80"]),
    ("item-8", "cat-plats", "Entrecôte Grillée 300g", "Pièce de bœuf française grillée, servie avec frites maison et beurre maître d'hôtel.", 24.0, "AVAILABLE", False, True, 18, ["https://images.unsplash.com/photo-1600891964092-4316c288032e?auto=format&fit=crop&w=800&q=80"]),
    ("item-9", "cat-plats", "Risotto aux Champignons Sauvages", "Riz Arborio, poêlée de cèpes et girolles, parsemé de parmesan et huile de truffe.", 17.0, "AVAILABLE", True, True, 20, ["https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=800&q=80"]),
    ("item-10", "cat-plats", "Pâtes Carbonara Traditionnelles", "Spaghetti, guanciale croustillant, jaune d'œuf, pecorino romano et poivre noir.", 14.5, "AVAILABLE", False, False, 12, ["https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=800&q=80"]),
    ("item-11", "cat-plats", "Curry Vert de Légumes Tofu", "Tofu poêlé, brocolis, pois gourmands et lait de coco au curry vert, riz basmati.", 15.5, "HIDDEN", True, True, 15, ["https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=800&q=80"]),
    ("item-12", "cat-desserts", "Tiramisu Classique", "Biscuit cuillère imbibé de café expresso, crème mascarpone et cacao amer.", 7.0, "AVAILABLE", True, False, 5, ["https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80"]),
    ("item-13", "cat-desserts", "Fondant au Chocolat", "Cœur coulant au chocolat noir 70%, servi tiède avec une boule de glace vanille.", 8.0, "AVAILABLE", True, False, 10, ["https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80"]),
    ("item-14", "cat-desserts", "Cheesecake Fruits Rouges", "Cheesecake style New-Yorkais sur biscuit spéculoos avec coulis de framboise.", 7.5, "OUT_OF_STOCK", True, False, 5, ["https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80"]),
    ("item-15", "cat-desserts", "Café Gourmand", "Un café expresso accompagné de 3 mini desserts du chef.", 8.5, "AVAILABLE", True, False, 5, ["https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80"]),
    ("item-16", "cat-boissons", "Limonade Artisanale", "Citron pressé, eau pétillante, sirop de sucre de canne et menthe fraîche.", 4.5, "AVAILABLE", True, True, 3, ["https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80"]),
    ("item-17", "cat-boissons", "Jus d'Orange Pressé", "Oranges fraîches pressées à la minute (25cl).", 4.0, "AVAILABLE", True, True, 3, ["https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80"]),
    ("item-18", "cat-boissons", "Bière Artisanale IPA (33cl)", "Bière blonde houblonnée aux notes d'agrumes et de fruits tropicaux.", 6.5, "AVAILABLE", True, False, 2, ["https://images.unsplash.com/photo-1608270586620-248524c67de9?auto=format&fit=crop&w=800&q=80"]),
    ("item-19", "cat-boissons", "Verre de Bordeaux Rouge (12cl)", "AOC Bordeaux Supérieur, notes de fruits noirs et épices douce.", 5.5, "AVAILABLE", True, True, 2, ["https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80"]),
    ("item-20", "cat-boissons", "Eau Minérale Pétillante (75cl)", "Bouteille en verre San Pellegrino.", 5.0, "AVAILABLE", True, True, 1, ["https://images.unsplash.com/photo-1560023907-5f339617ea30?auto=format&fit=crop&w=800&q=80"]),
]

# Mix of statuses for realistic dashboard
# Past days: mostly completed with a few cancelled orders/day.
PAST_ORDER_STATUSES = [
    "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED",
    "CANCELLED",
]

# Today: active mix so ordersToday / pendingOrders / revenueToday are non-zero.
TODAY_ORDER_STATUSES = [
    "CONFIRMED", "PREPARING", "PREPARING", "READY", "PENDING", "COMPLETED",
]

ORDER_TYPES = [
    "EAT_IN", "TAKEAWAY", "EAT_IN", "EAT_IN", "DELIVERY",
    "EAT_IN", "TAKEAWAY", "EAT_IN", "EAT_IN", "TAKEAWAY",
    "EAT_IN", "DELIVERY", "EAT_IN", "TAKEAWAY", "EAT_IN",
    "DELIVERY", "EAT_IN", "TAKEAWAY", "EAT_IN", "EAT_IN",
]

RESERVATION_TIMES = [
    time(12, 0), time(12, 0), time(13, 0), time(19, 0), time(19, 0),
    time(20, 0), time(20, 0), time(12, 0), time(12, 0), time(13, 0),
    time(19, 0), time(20, 0), time(12, 0), time(13, 0), time(19, 0),
    time(20, 0), time(12, 0), time(20, 0), time(19, 0), time(20, 0),
]

# Relative days (0 = today, negative = past, positive = future) biased so the
# grid home page (today) and the next few evenings look busy.
RESERVATION_DAY_OFFSETS = [
    0, 0, 0, 0, 0, 0,             # today: dense for the day grid
    1, 1, 1, 1,                   # tomorrow
    -1, -1, -1, -1,               # yesterday
    2, 2, 2, -2, -2, -2,          # +/- 2 days
    3, 3, 3, -3, -3, -3,          # +/- 3 days
    4, 4, -4, -4, 5, 5, -5, -5,   # +/- 4-5 days
    6, 6, -6, -6,                 # +/- 6 days
    7, 7, -7, -7,                 # +/- 7 days
    8, 8, -8, -8,                 # +/- 8 days
    9, -9, 10, 11, -10, -11,      # spread over the rest of the month
]


def create_customer_records(session: Session):
    customers = {}
    for idx, (cid, first, last, email, phone, status, points, tier, discount, prefs) in enumerate(CUSTOMERS):
        customer = Customer(
            id=cid,
            firstName=first,
            lastName=last,
            email=email,
            phone=phone,
            image=CUSTOMER_IMAGES[idx % len(CUSTOMER_IMAGES)],
            status=status,
            totalOrders=0,
            totalReservations=0,
            noShowCount=0,
            totalSpent=0.0,
        )
        loyalty = CustomerLoyalty(
            id=f"{cid}-loyalty",
            customerId=cid,
            points=points,
            tier=tier,
            customDiscountPercent=discount,
        )
        preferences = CustomerPreferences(
            id=f"{cid}-prefs",
            customerId=cid,
            isVegetarian=prefs.get("isVegetarian", False),
            isGlutenFree=prefs.get("isGlutenFree", False),
            allergies=prefs.get("allergies") or [],
            preferredTableNotes=prefs.get("preferredTableNotes"),
        )
        session.add(customer)
        session.add(loyalty)
        session.add(preferences)
        customers[cid] = {"customer": customer, "loyalty": loyalty}
    return customers


def create_menu_items(session: Session):
    items = {}
    for iid, cat_id, name, desc, price, status, veg, gf, prep, images in MENU_ITEMS:
        item = MenuItem(
            id=iid,
            categoryId=cat_id,
            name=name,
            description=desc,
            price=price,
            imageUrl=images,
            status=status,
            isVegetarian=veg,
            isGlutenFree=gf,
            preparationTimeMinutes=prep,
            isActive=True,
        )
        session.add(item)
        items[iid] = item

    # Option groups for burgers & steak (item-5 and item-8)
    group1 = MenuOptionGroup(
        id="optg-burger-cuisson",
        menuItemId="item-5",
        name="Cuisson du steak",
        required=True,
        minChoices=1,
        maxChoices=1,
    )
    group2 = MenuOptionGroup(
        id="optg-burger-supps",
        menuItemId="item-5",
        name="Suppléments",
        required=False,
        minChoices=0,
        maxChoices=2,
    )
    group3 = MenuOptionGroup(
        id="optg-steak-sauce",
        menuItemId="item-8",
        name="Sauce",
        required=True,
        minChoices=1,
        maxChoices=1,
    )
    session.add(group1)
    session.add(group2)
    session.add(group3)
    session.flush()

    option_rows = [
        ("opt-1", "optg-burger-cuisson", "Saignant", 0.0),
        ("opt-2", "optg-burger-cuisson", "À point", 0.0),
        ("opt-3", "optg-burger-cuisson", "Bien cuit", 0.0),
        ("opt-4", "optg-burger-supps", "Double fromage", 1.5),
        ("opt-5", "optg-burger-supps", "Bacon extra", 2.0),
        ("opt-6", "optg-steak-sauce", "Sauce Poivre", 0.0),
        ("opt-7", "optg-steak-sauce", "Sauce Béarnaise", 0.0),
        ("opt-8", "optg-steak-sauce", "Sauce Roquefort", 1.0),
    ]
    for oid, gid, name, extra in option_rows:
        session.add(MenuOption(id=oid, optionGroupId=gid, name=name, priceExtra=extra))
    return items


def create_orders(session: Session, customers: dict, items: dict):
    promo_by_code = {p.code: p for p in session.exec(select(PromoCode)).all()}
    table_ids = session.exec(select(RestaurantTable)).all()

    # item combinations per order
    order_menu_sets = [
        [("item-5", 2, "Bien cuit pour l'un"), ("item-18", 2, None)],
        [("item-7", 1, "Sauce à part (sans arachides)"), ("item-17", 1, None)],
        [("item-9", 2, "Sans lactose s'il vous plaît"), ("item-12", 2, None)],
        [("item-8", 1, None)],
        [("item-10", 2, "Piment moyen")],
        [("item-5", 1, None)],
        [("item-6", 2, None)],
        [("item-13", 1, None), ("item-16", 2, None)],
        [("item-8", 1, None), ("item-19", 1, None)],
        [("item-12", 1, None), ("item-18", 1, None)],
        [("item-7", 2, "STRICTEMENT SANS GLUTEN")],
        [("item-5", 3, None)],
        [("item-6", 4, None)],
        [("item-9", 1, "Attention allergie fruits à coque")],
        [("item-12", 2, None)],
        [("item-15", 1, None)],
        [("item-8", 1, "Cuisson à point")],
        [("item-3", 1, None)],
        [("item-5", 2, None)],
        [("item-7", 1, None), ("item-12", 1, None)],
    ]

    # promo mapping for some orders (cycled)
    order_promos = [
        None, "promo-welcome", "promo-gold", "promo-chef", "promo-welcome",
        None, None, None, "promo-vip", None,
        None, "promo-chef", "promo-gold", None, None,
        None, None, "promo-vip", None, None,
    ]

    now = datetime.utcnow()
    customers_rec = [customers[cid]["customer"] for cid, *_ in CUSTOMERS]

    # 6 orders per day over the last 15 days (today included) => 90 orders.
    orders = []
    total = 0
    for day in range(15):
        statuses = TODAY_ORDER_STATUSES if day == 0 else PAST_ORDER_STATUSES
        for slot, status in enumerate(statuses):
            i = total
            total += 1
            otype = ORDER_TYPES[i % len(ORDER_TYPES)]
            customer = customers_rec[i % len(customers_rec)]
            promo_id = order_promos[(day * 3 + slot) % len(order_promos)]

            # Times: spread across the day without going past now for today.
            if day == 0:
                latest = max(7, now.hour - 1)
                hour = min(8 + slot, latest)
            else:
                hour = 9 + (slot * 2) % 8
            created_at = (now - timedelta(days=day)).replace(
                hour=hour,
                minute=(i * 7) % 60,
                second=0,
                microsecond=0,
            )

            items_payload = order_menu_sets[(day * 3 + slot) % len(order_menu_sets)]
            subtotal = 0.0
            order_items = []
            for menu_item_id, qty, notes in items_payload:
                menu_item = items[menu_item_id]
                line_total = round(menu_item.price * qty, 2)
                subtotal += line_total
                order_items.append(
                    OrderItem(
                        id=f"oi-{i + 1:03d}-{menu_item_id}",
                        menuItemId=menu_item_id,
                        quantity=qty,
                        totalPrice=line_total,
                        notes=notes,
                        createdAt=created_at,
                    )
                )

            discount_amount = 0.0
            if promo_id:
                promo = session.get(PromoCode, promo_id)
                if promo:
                    if promo.discountType == "PERCENTAGE":
                        discount_amount = round(subtotal * (promo.discountValue / 100), 2)
                    else:
                        discount_amount = min(promo.discountValue, subtotal)
                    if promo.maxDiscountAmount:
                        discount_amount = min(discount_amount, promo.maxDiscountAmount)
                    promo.usageCount += 1

            taxed_base = subtotal - discount_amount
            total_amount = round(taxed_base, 2)

            table = table_ids[i % len(table_ids)] if otype == "EAT_IN" else None
            payment_status = (
                PAYMENTSTATUS.REFUNDED
                if status == "CANCELLED"
                else PAYMENTSTATUS.PAID if (i % 3 != 0) else PAYMENTSTATUS.UNPAID
            )
            payment_method = (
                None
                if payment_status == PAYMENTSTATUS.UNPAID
                else [PAYMENTMETHOD.CARD, PAYMENTMETHOD.CASH, PAYMENTMETHOD.MOBILE_MONEY][i % 3]
            )
            completed_at = (
                created_at + timedelta(minutes=40 + (slot * 13))
                if status == "COMPLETED"
                else None
            )

            order = Order(
                id=f"ord-{i + 1:03d}",
                orderNumber=f"CMD-{101 + i}",
                type=otype,
                status=status,
                customerId=customer.id,
                tableId=table.id if table else None,
                discountAmount=discount_amount,
                appliedPromoId=promo_id,
                taxAmount=0.0,
                totalAmount=total_amount,
                paymentStatus=payment_status,
                paymentMethod=payment_method.value if payment_method else None,
                estimatedPreparationTimeMinutes=15 + (i % 15),
                completedAt=completed_at,
                createdAt=created_at,
                updatedAt=created_at + timedelta(minutes=20),
            )
            session.add(order)
            orders.append(order)
            # attach orderId to items
            for oi in order_items:
                oi.orderId = order.id
                session.add(oi)

            # update customer aggregate stats
            customer.totalOrders += 1
            if status != "CANCELLED":
                customer.totalSpent = round(customer.totalSpent + total_amount, 2)
            customer.lastVisitAt = created_at
            # update loyalty points
            loyalty = customers[customer.id]["loyalty"]
            if status == "COMPLETED":
                loyalty.points += int(total_amount)

    return orders


def create_reservations(session: Session, customers: dict):
    table_ids = session.exec(select(RestaurantTable)).all()
    customers_rec = [customers[cid]["customer"] for cid, *_ in CUSTOMERS]
    today = datetime.utcnow().date()
    now = datetime.utcnow()
    reservations = []

    for i, offset in enumerate(RESERVATION_DAY_OFFSETS):
        customer = customers_rec[i % len(customers_rec)]
        reserve_date = today + timedelta(days=offset)

        # Past dates are closed; today & future mix pending/confirmed.
        if offset < 0:
            status = "CANCELLED" if i % 6 == 2 else "COMPLETED"
        else:
            if i % 7 == 0:
                status = "CANCELLED"
            elif i % 3 == 0:
                status = "PENDING"
            else:
                status = "CONFIRMED"

        table_id = table_ids[i % len(table_ids)].id if (i % 4 != 1) else None

        reservation = Reservation(
            id=f"res-{i + 1:03d}",
            customerId=customer.id,
            tableId=table_id,
            reservationDate=reserve_date,
            reservationTime=RESERVATION_TIMES[i % len(RESERVATION_TIMES)],
            numberOfGuests=[2, 4, 8, 5, 2][i % 5],
            status=status,
            specialRequest=None if i % 3 == 0 else "Demande spéciale",
            createdAt=now - timedelta(days=4 + (i % 5), hours=i % 12),
            updatedAt=now - timedelta(days=2 + (i % 3), hours=(i % 6)),
        )
        session.add(reservation)
        reservations.append(reservation)
        customer.totalReservations += 1

    return reservations


def update_table_statuses(session: Session, orders: list, reservations: list):
    """Mark tables occupied/reserved based on today's live orders & reservations."""
    today = datetime.utcnow().date()
    now_time = datetime.utcnow().time()
    table_by_id = {t.id: t for t in session.exec(select(RestaurantTable)).all()}

    reserved_ids = {
        r.tableId
        for r in reservations
        if r.tableId
        and r.reservationDate == today
        and r.status in ("PENDING", "CONFIRMED")
        and r.reservationTime >= now_time
    }
    occupied_ids = {
        o.tableId
        for o in orders
        if o.tableId
        and o.createdAt.date() == today
        and o.status not in ("COMPLETED", "CANCELLED")
    }

    for tid, table in table_by_id.items():
        if tid in reserved_ids:
            table.status = TABLESTATUS.RESERVED
        elif tid in occupied_ids:
            table.status = TABLESTATUS.OCCUPIED
        elif tid == "tbl-020":
            table.status = TABLESTATUS.UNAVAILABLE
        else:
            table.status = TABLESTATUS.AVAILABLE


def seed(fresh: bool = False):
    if fresh:
        with engine.begin() as conn:
            conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        print("Dropped all tables")

    SQLModel.metadata.create_all(engine)
    print("Tables ready")

    with Session(engine) as session:
        # clear existing rows if any (non-fresh reruns)
        for model in [OrderItem, Order, Reservation, MenuOption, MenuOptionGroup,
                      MenuItem, CustomerPreferences, CustomerLoyalty, Customer,
                      RestaurantTable, PromoCode, Category]:
            rows = session.exec(select(model)).all()
            for r in rows:
                session.delete(r)
        session.commit()
        print("Cleared existing data")

        # Categories
        for c in CATEGORIES:
            session.add(Category(id=c["id"], name=c["name"], description=c["description"]))
        session.commit()
        print("Seeded categories:", len(CATEGORIES))

        # Promo codes
        for p in PROMO_CODES:
            session.add(PromoCode(**p))
        session.commit()
        print("Seeded promo codes:", len(PROMO_CODES))

        # Tables
        for i in range(20):
            session.add(
                RestaurantTable(
                    id=f"tbl-{i + 1:03d}",
                    num=i + 1,
                    capacity=TABLE_CAPACITIES[i],
                    place=TABLE_PLACES[i],
                    status=TABLESTATUS.AVAILABLE,
                )
            )
        session.commit()
        print("Seeded tables: 20")

        # Customers
        customers = create_customer_records(session)
        session.commit()
        print("Seeded customers:", len(customers))

        # Menu items
        items = create_menu_items(session)
        session.commit()
        print("Seeded menu items:", len(items))

        # Orders
        orders = create_orders(session, customers, items)
        session.commit()
        print("Seeded orders:", len(orders))

        # Reservations
        reservations = create_reservations(session, customers)
        session.commit()
        print("Seeded reservations:", len(reservations))

        # Tables statuses reflecting today's activity
        update_table_statuses(session, orders, reservations)
        session.commit()
        print("Updated table statuses")

    print("Seed complete.")


if __name__ == "__main__":
    seed(fresh="--fresh" in sys.argv)