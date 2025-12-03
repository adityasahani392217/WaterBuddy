import streamlit as st
import datetime
import random
import os
from PIL import Image, ImageDraw

# ===== GLOBAL SETTINGS =====
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

# ===== INITIALIZATION =====
def init_state():
    """Initialize session state variables if they don't exist."""
    defaults = {
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
        "current_intake": 0,
        "daily_goal": 2500,
        "data_loaded": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ===== FILE OPERATIONS =====
def load_data():
    """Load data from the text file into session state."""
    if not os.path.exists(DATA_FILE):
        return  # Start fresh if file doesn't exist

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()

        is_history = False
        history_data = {}

        for line in lines:
            line = line.strip()
            if not line: continue

            if line == "[HISTORY]":
                is_history = True
                continue

            if not is_history:
                if "=" in line:
                    k, v = line.split("=", 1)
                    # Convert Booleans
                    if k in ["use_weight", "use_custom", "dark_mode",
                             "has_glasses", "has_crown", "has_bowtie", "has_partyhat"]:
                        st.session_state[k] = (v == "True")
                    # Convert Integers
                    elif k in ["xp", "level", "current_intake", "daily_goal"]:
                        st.session_state[k] = int(v)
                    # Load Strings
                    elif k in st.session_state:
                        st.session_state[k] = v
            else:
                # Load History Lines: date|intake|goal
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) == 3:
                        d, intake, goal = parts
                        history_data[d] = {"intake": int(intake), "goal": int(goal)}
        
        st.session_state.history = history_data
        
        # Restore today's intake if it exists in history logic
        today = str(datetime.date.today())
        if today in st.session_state.history:
            st.session_state.current_intake = st.session_state.history[today]["intake"]
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

def save_data():
    """Save current session state to the text file."""
    try:
        with open(DATA_FILE, "w") as f:
            # Save settings
            keys = ["xp", "level", "age", "weight", "use_weight", "use_custom", 
                    "custom_goal", "dark_mode", "has_glasses", "has_crown", 
                    "has_bowtie", "has_partyhat", "daily_goal"]
            
            for k in keys:
                f.write(f"{k}={st.session_state[k]}\n")

            # Save History
            f.write("\n[HISTORY]\n")
            for date, h in st.session_state.history.items():
                f.write(f"{date}|{h['intake']}|{h['goal']}\n")
                
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ===== MASCOT GENERATOR =====
def draw_mascot(pct):
    """Draws the mascot dynamically using PIL based on progress percentage."""
    # Create transparent canvas
    img = Image.new("RGBA", (400, 400), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    # 1. Visual Feedback: Water Level Background
    # Calculates height: 300 is bottom, 100 is top.
    water_height = int(300 - (200 * min(1.0, pct))) 
    d.rectangle([100, water_height, 300, 280], fill="#e0f2fe") 

    # 2. Face Color Logic (Gamification)
    if pct > 1: face_color = "#8b5cf6"       # Purple (Overachiever)
    elif pct == 1: face_color = "#FFD700"    # Gold (Goal Met)
    elif pct >= 0.5: face_color = "#4ade80"  # Green (Good)
    else: face_color = "#60a5fa"             # Blue (Start)

    # Draw Face
    d.ellipse((100, 80, 300, 280), fill=face_color, outline="black", width=4)

    # 3. Eyes / Sunglasses Logic
    if pct >= 1 or st.session_state.has_glasses:
        # Draw Sunglasses
        d.rectangle((150, 130, 180, 160), fill="black")
        d.rectangle((220, 130, 250, 160), fill="black")
        d.line((180, 145, 220, 145), fill="black", width=4)
    else:
        # Draw Normal Eyes
        d.ellipse((155, 135, 170, 150), fill="black")
        d.ellipse((230, 135, 245, 150), fill="black")

    # 4. Mouth Logic
    if pct >= 1:
        d.arc((150, 160, 250, 220), 0, 180, fill="black", width=4) # Big Smile
    elif pct >= 0.5:
        d.arc((150, 170, 250, 230), 0, 180, fill="black", width=4) # Smile
    else:
        d.line((170, 210, 230, 210), fill="black", width=4) # Neutral

    # 5. Accessories (Shop Items)
    if st.session_state.has_crown:
        d.polygon([(160, 60), (190, 110), (210, 60), (230, 110), (260, 60)], fill="#fbbf24", outline="black")

    if st.session_state.has_bowtie:
        d.polygon([(180, 260), (150, 280), (180, 300)], fill="red", outline="black")
        d.polygon([(220, 260), (250, 280), (220, 300)], fill="red", outline="black")

    if st.session_state.has_partyhat:
        d.polygon([(200, 20), (170, 90), (230, 90)], fill="#ec4899", outline="black")

    return img

# ===== CORE LOGIC =====
def recalc_goal():
    """Recalculates daily goal based on settings."""
    d = st.session_state
    if d.use_custom:
        try: d.daily_goal = int(d.custom_goal)
        except: d.daily_goal = 2500
    elif d.use_weight:
        try: d.daily_goal = int(d.weight) * 35
        except: d.daily_goal = 2500
    else:
        d.daily_goal = AGE_GUIDELINES.get(d.age, 2500)
    
    save_data()

def add_xp(amount):
    """Adds XP and handles leveling up."""
    st.session_state.xp += amount
    new_level = 1 + st.session_state.xp // XP_PER_LEVEL
    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.balloons() # Visual celebration
        st.toast(f"🎉 Level Up! You are now Level {new_level}!")
    save_data()

def add_water(amount):
    """Adds water, updates XP, and saves history."""
    st.session_state.current_intake += amount
    add_xp(amount // 10) # 10% of ml becomes XP
    
    # Update History for Today
    today = str(datetime.date.today())
    st.session_state.history[today] = {
        "intake": st.session_state.current_intake,
        "goal": st.session_state.daily_goal
    }
    save_data()

def reset_day():
    """Resets daily progress but keeps XP/Items."""
    st.session_state.current_intake = 0
    today = str(datetime.date.today())
    if today in st.session_state.history:
        st.session_state.history[today]["intake"] = 0
    save_data()
    st.rerun()

# ===== MAIN APP EXECUTION =====
st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="wide")
init_state()

# Load data only once per session launch
if not st.session_state.data_loaded:
    load_data()
    recalc_goal()
    st.session_state.data_loaded = True

# ===== SIDEBAR (SETTINGS) =====
with st.sidebar:
    st.title("⚙️ Settings")
    
    st.subheader("1. Profile")
    # Finds current age index to set default value
    current_index = list(AGE_GUIDELINES.keys()).index(st.session_state.age)
    new_age = st.selectbox("Age Group", AGE_GUIDELINES.keys(), index=current_index)
    if new_age != st.session_state.age:
        st.session_state.age = new_age
        recalc_goal()
        st.rerun()

    st.subheader("2. Goal Calculation")
    use_weight = st.checkbox("Calculate by Weight", st.session_state.use_weight)
    if use_weight:
        w_input = st.text_input("Weight (kg)", st.session_state.weight)
        if w_input != st.session_state.weight or use_weight != st.session_state.use_weight:
            st.session_state.weight = w_input
            st.session_state.use_weight = use_weight
            recalc_goal()
            st.rerun()
            
    use_custom = st.checkbox("Manual Goal", st.session_state.use_custom)
    if use_custom:
        c_input = st.text_input("Custom Goal (ml)", st.session_state.custom_goal)
        if c_input != st.session_state.custom_goal or use_custom != st.session_state.use_custom:
            st.session_state.custom_goal = c_input
            st.session_state.use_custom = use_custom
            recalc_goal()
            st.rerun()

    st.divider()
    if st.button("🗑️ Reset Daily Progress"):
        reset_day()
        
    if st.button("💡 Get Hydration Tip"):
        st.toast(random.choice(HYDRATION_TIPS), icon="💡")

# ===== MAIN DASHBOARD =====
st.title("💧 WaterBuddy")
st.markdown(f"**Level {st.session_state.level}** | XP: {st.session_state.xp}")

# 1. Metrics Row
m1, m2, m3 = st.columns(3)
m1.metric("Target", f"{st.session_state.daily_goal} ml")
m2.metric("Drank", f"{st.session_state.current_intake} ml", delta=f"{st.session_state.current_intake} ml")
remaining = max(0, st.session_state.daily_goal - st.session_state.current_intake)
m3.metric("Remaining", f"{remaining} ml", delta_color="inverse")

# 2. Visuals & Controls Row
col_img, col_act = st.columns([1, 1.5])

with col_img:
    # Calculate percentage safely
    pct = st.session_state.current_intake / st.session_state.daily_goal if st.session_state.daily_goal else 0
    st.image(draw_mascot(pct), caption="Your Hydration Companion", width=350)

with col_act:
    st.subheader("Log Water")
    st.progress(min(1.0, pct))
    
    # Quick Add Buttons
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("+100 ml"): add_water(100); st.rerun()
    if b2.button("+250 ml"): add_water(250); st.rerun()
    if b3.button("+500 ml"): add_water(500); st.rerun()
    if b4.button("+1 L"): add_water(1000); st.rerun()
    
    with st.expander("Custom Amount"):
        c_amt = st.number_input("Amount (ml)", min_value=1, step=50)
        if st.button("Add"):
            add_water(int(c_amt))
            st.rerun()

# 3. Shop Section (Gamification)
st.divider()
st.subheader("🛍️ The XP Shop")

def shop_button(col, cost, key, name, emoji):
    """Helper function to create shop buttons."""
    if st.session_state[key]:
        # If owned, button removes it
        if col.button(f"❌ Remove {name}"):
            st.session_state[key] = False
            save_data()
            st.rerun()
    else:
        # If not owned, buy it
        if col.button(f"{emoji} Buy {name} ({cost} XP)"):
            if st.session_state.xp >= cost:
                st.session_state.xp -= cost
                st.session_state[key] = True
                save_data()
                st.balloons()
                st.rerun()
            else:
                st.error("Not enough XP!")

s1, s2, s3, s4 = st.columns(4)
shop_button(s1, 150, "has_bowtie", "Bow Tie", "🎀")
shop_button(s2, 200, "has_glasses", "Glasses", "😎")
shop_button(s3, 500, "has_crown", "Crown", "👑")
shop_button(s4, 1000, "has_partyhat", "Party Hat", "🎉")

# 4. History Log
with st.expander("📅 View Hydration History"):
    if st.session_state.history:
        for date, data in sorted(st.session_state.history.items(), reverse=True):
            status = "✅ Goal Met" if data['intake'] >= data['goal'] else "⚠️ Missed"
            st.write(f"**{date}**: {data['intake']} / {data['goal']} ml — {status}")
    else:
        st.info("No history yet. Start drinking water!")
