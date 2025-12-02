import streamlit as st
import datetime
import random
from PIL import Image, ImageDraw

# ===== WATERBUDDY ORIGINAL SETTINGS =====
AGE_GUIDELINES = {
    "Child (4-8)": 1200,
    "Teen (9-13)": 1700,
    "Adult (14-64)": 2500,
    "Senior (65+)": 1700,
}

HYDRATION_TIPS = [
    "Sip water regularly instead of chugging.",
    "Keep a water bottle near your study or work desk.",
    "Drink one glass of water with every meal.",
    "Thirst is a late sign—drink before you feel thirsty.",
    "Water helps with focus, mood, and energy.",
    "Add lemon or cucumber slices for taste.",
    "Check your urine color; pale yellow is ideal.",
    "Eat water-rich foods like watermelon and cucumber."
]

DATA_FILE = "water_buddy_data.txt"
XP_PER_LEVEL = 1000


# ===== LOAD & SAVE DATA (unchanged logic, Streamlit-compatible) =====
def load_data():
    data = {
        "xp": 0,
        "level": 1,
        "age": "Adult (14-64)",
        "weight": "70",
        "use_weight": False,
        "use_custom": False,
        "custom_goal": "2500",
        "dark_mode": False,
        "has_glasses": False,
        "has_crown": False,
        "has_bowtie": False,
        "has_partyhat": False,
        "history": {},
        "current_intake": 0
    }

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()

        is_history = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line == "[HISTORY]":
                is_history = True
                continue

            if not is_history:
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k in ["use_weight", "use_custom", "dark_mode",
                             "has_glasses", "has_crown", "has_bowtie", "has_partyhat"]:
                        data[k] = (v == "True")
                    elif k in ["xp", "level"]:
                        data[k] = int(v)
                    else:
                        data[k] = v
            else:
                if "|" in line:
                    d, intake, goal = line.split("|")
                    data["history"][d] = {
                        "intake": int(intake),
                        "goal": int(goal)
                    }

        # Restore today's intake
        today = str(datetime.date.today())
        if today in data["history"]:
            data["current_intake"] = data["history"][today]["intake"]

    except:
        pass

    return data


def save_data():
    d = st.session_state
    try:
        with open(DATA_FILE, "w") as f:
            f.write(f"xp={d.xp}\n")
            f.write(f"level={d.level}\n")
            f.write(f"age={d.age}\n")
            f.write(f"weight={d.weight}\n")
            f.write(f"use_weight={d.use_weight}\n")
            f.write(f"use_custom={d.use_custom}\n")
            f.write(f"custom_goal={d.custom_goal}\n")
            f.write(f"dark_mode={d.dark_mode}\n")
            f.write(f"has_glasses={d.has_glasses}\n")
            f.write(f"has_crown={d.has_crown}\n")
            f.write(f"has_bowtie={d.has_bowtie}\n")
            f.write(f"has_partyhat={d.has_partyhat}\n")

            f.write("\n[HISTORY]\n")
            for date, h in d.history.items():
                f.write(f"{date}|{h['intake']}|{h['goal']}\n")

    except Exception as e:
        st.error(f"Error saving: {e}")


# ===== DRAW MASCOT =====
def draw_mascot(pct):
    img = Image.new("RGBA", (400, 400), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    # Mascot color logic
    if pct > 1:
        face = "#8b5cf6"
    elif pct == 1:
        face = "#FFD700"
    elif pct >= 0.5:
        face = "#4ade80"
    else:
        face = "#60a5fa"

    d.ellipse((100, 80, 300, 280), fill=face, outline="black", width=4)

    # Eyes / sunglasses
    if pct >= 1 or st.session_state.has_glasses:
        d.rectangle((150, 130, 180, 160), fill="black")
        d.rectangle((220, 130, 250, 160), fill="black")
        d.line((180, 145, 220, 145), fill="black", width=4)
    else:
        d.ellipse((155, 135, 170, 150), fill="black")
        d.ellipse((230, 135, 245, 150), fill="black")

    # Mouth
    if pct >= 1:
        d.arc((150, 160, 250, 220), 0, 180, fill="black", width=4)
    elif pct >= 0.5:
        d.arc((150, 170, 250, 230), 0, 180, fill="black", width=4)
    else:
        d.line((170, 210, 230, 210), fill="black", width=4)

    # Accessories
    if st.session_state.has_crown:
        d.polygon([(160, 60), (190, 110), (210, 60), (230, 110), (260, 60)], fill="#fbbf24")

    if st.session_state.has_bowtie:
        d.polygon([(180, 260), (150, 280), (180, 300)], fill="red")
        d.polygon([(220, 260), (250, 280), (220, 300)], fill="red")

    if st.session_state.has_partyhat:
        d.polygon([(200, 20), (170, 90), (230, 90)], fill="#ec4899")

    return img


# ===== CALCULATE GOAL SAFELY =====
def recalc_goal():
    d = st.session_state

    if d.use_custom:
        try:
            d.daily_goal = int(d.custom_goal)
        except:
            d.daily_goal = 2500
    elif d.use_weight:
        try:
            d.daily_goal = int(d.weight) * 35
        except:
            d.daily_goal = 2500
    else:
        d.daily_goal = AGE_GUIDELINES.get(d.age, 2500)

    update_history()
    save_data()


# ===== XP, WATER, HISTORY =====
def add_xp(amount):
    st.session_state.xp += amount
    new_level = 1 + st.session_state.xp // XP_PER_LEVEL

    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.success(f"🎉 Level Up! Now Level {new_level}!")

    save_data()


def add_water(amount):
    st.session_state.current_intake += amount
    add_xp(amount // 10)
    update_history()
    save_data()


def update_history():
    today = str(datetime.date.today())
    st.session_state.history[today] = {
        "intake": st.session_state.current_intake,
        "goal": st.session_state.daily_goal
    }


def reset_day():
    st.session_state.current_intake = 0
    update_history()
    save_data()


# ===== STREAMLIT UI =====
st.set_page_config(page_title="WaterBuddy Streamlit", layout="wide")

# Load data on first launch
if "loaded" not in st.session_state:
    loaded = load_data()
    for k, v in loaded.items():
        st.session_state[k] = v
    recalc_goal()
    st.session_state.loaded = True


# ===== SIDEBAR =====
st.sidebar.title("WaterBuddy Controls")

st.sidebar.subheader("Goal Settings")
st.session_state.age = st.sidebar.selectbox("Age Group", AGE_GUIDELINES.keys())
st.session_state.weight = st.sidebar.text_input("Weight (kg)", st.session_state.weight)
st.session_state.use_weight = st.sidebar.checkbox("Use Weight Goal", st.session_state.use_weight)

st.session_state.custom_goal = st.sidebar.text_input("Custom Goal (ml)", st.session_state.custom_goal)
st.session_state.use_custom = st.sidebar.checkbox("Use Custom Goal", st.session_state.use_custom)

if st.sidebar.button("Apply Goal"):
    recalc_goal()

st.sidebar.subheader("Quick Add Water")
for amt in [100, 250, 500, 1000]:
    if st.sidebar.button(f"+{amt} ml"):
        add_water(amt)

custom_amt = st.sidebar.text_input("Add Custom Amount (ml)")
if st.sidebar.button("Add Custom"):
    try:
        add_water(int(custom_amt))
    except:
        st.sidebar.error("Enter a valid number.")

st.sidebar.divider()

if st.sidebar.button("💡 Hydration Tip"):
    st.sidebar.info(random.choice(HYDRATION_TIPS))

if st.sidebar.button("Reset Day"):
    reset_day()

st.sidebar.checkbox("Dark Mode", st.session_state.dark_mode)


# ===== MAIN UI =====
st.title("💧 WaterBuddy — Streamlit Edition")

cols = st.columns(3)
cols[0].metric("Daily Goal", f"{st.session_state.daily_goal} ml")
cols[1].metric("Current Intake", f"{st.session_state.current_intake} ml")
remaining = max(0, st.session_state.daily_goal - st.session_state.current_intake)
cols[2].metric("Remaining", f"{remaining} ml")

st.subheader(f"Level {st.session_state.level} | XP: {st.session_state.xp}")

pct = st.session_state.current_intake / st.session_state.daily_goal if st.session_state.daily_goal else 0
st.image(draw_mascot(pct), width=300)
st.progress(min(1.0, pct))


# ===== HISTORY =====
st.subheader("📅 History Log")

for date, h in sorted(st.session_state.history.items()):
    st.write(f"**{date}** — {h['intake']} ml / {h['goal']} ml")


# ===== SHOP =====
st.subheader("🎁 XP Shop")

colA, colB = st.columns(2)

def toggle_item(cost, key, name):
    if st.session_state[key]:
        st.session_state[key] = False
        st.success(f"{name} removed!")
        save_data()
        return

    if st.session_state.xp >= cost:
        st.session_state.xp -= cost
        st.session_state[key] = True
        st.success(f"Purchased {name}!")
        save_data()
    else:
        st.error("Not enough XP.")


if colA.button("😎 Sunglasses — 200 XP"):
    toggle_item(200, "has_glasses", "Sunglasses")

if colA.button("👑 Crown — 500 XP"):
    toggle_item(500, "has_crown", "Crown")

if colB.button("🎀 Bow Tie — 150 XP"):
    toggle_item(150, "has_bowtie", "Bow Tie")

if colB.button("🎉 Party Hat — 1000 XP"):
    toggle_item(1000, "has_partyhat", "Party Hat")
