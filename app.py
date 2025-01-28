import streamlit as st
import json
import requests
from openai import OpenAI 

# --- Load World Data ---
@st.cache_resource  # Cache to load only once
def load_world_data(json_file_path):
    if json_file_path.startswith("http"):
        response = requests.get(json_file_path)
        response.raise_for_status()  # Ensure request is successful
        world_data = response.json()  # Parse JSON response
    else:
        with open(json_file_path, 'r') as f:
            world_data = json.load(f)
    return world_data

# --- API Interaction Function (Adapt from your example) ---
def generate_response(messages, api_key, provider, temperature):
    if not api_key: # Check for API key here to avoid initial message
        return "API key not configured. Please set it in Streamlit secrets."
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1") # Deepseek API base URL
        response = client.chat.completions.create(
            model="deepseek-chat",  # Or "deepseek-reasoner", experiment with models
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


# --- Game Logic Functions ---
def start_game(world_data):
    st.session_state.world_data = world_data
    st.session_state.inventory = {}
    st.session_state.current_station = "New Eden"  # Example starting station
    st.session_state.current_town = "Verdant Spire"  # Example starting town

    initial_prompt_content = f"""You are the Dungeon Master for a text-based RPG set in the world of {world_data['name']}.
    The world description is: {world_data['description']}.

    The player starts in {st.session_state.current_town} in {st.session_state.current_station}.
    Station Description: {world_data['stations'][st.session_state.current_station]['description']}.
    Town Description: {world_data['stations'][st.session_state.current_station]['towns'][st.session_state.current_town]['description']}.
    Available NPCs in {st.session_state.current_town}:
    """
    if 'npcs' in world_data['stations'][st.session_state.current_station]['towns'][st.session_state.current_town]:
        for npc_name, npc_data in world_data['stations'][st.session_state.current_station]['towns'][st.session_state.current_town]['npcs'].items():
            initial_prompt_content += f"- {npc_data['name']}: {npc_data['description']}\n"
    else:
        initial_prompt_content += "None visible.\n"

    initial_prompt_content += """
    Describe the player's immediate surroundings in {st.session_state.current_town} and wait for their first command.
    Keep your descriptions evocative and engaging, setting the scene for an immersive role-playing experience.
    Remember to act as the Dungeon Master and guide the player through the world. Aim to keep your initial description to around 200 words.
    """

    initial_messages = [
        {"role": "system", "content": "You are a Dungeon Master for a text-based RPG. Use the provided world data to describe locations, NPCs, and events. Be creative and engaging. Keep responses concise, aiming for approximately 200 words."},
        {"role": "user", "content": initial_prompt_content} # Send the initial prompt as a user message to trigger the DM response
    ]

    initial_response = generate_response(initial_messages, st.session_state.api_key, st.session_state.api_provider, st.session_state.temperature)

    st.session_state.messages = [
        {"role": "system", "content": "You are a Dungeon Master for a text-based RPG. Use the provided world data to describe locations, NPCs, and events. Be creative and engaging. Keep responses concise, aiming for approximately 200 words."},
        {"role": "assistant", "content": initial_response if initial_response and not initial_response.startswith("API key not configured") else "Welcome to Aurora Nexus!"} # Display the AI's response as the first message, or default welcome if API key issue or no response
    ]


def get_location_description(game_state):
    world_data = game_state.world_data
    station_name = game_state.current_station
    town_name = game_state.current_town
    town_data = world_data['stations'][station_name]['towns'][town_name]
    description = f"**{town_data['name']}:** {town_data['description']}\n\n"
    npc_names = [npc['name'] for npc in town_data['npcs'].values()] if 'npcs' in town_data else []
    if npc_names:
        description += f"**Notable inhabitants you see around you:** {', '.join([npc['name'] for npc in town_data['npcs'].values()])}.\n"
    return description

def handle_player_input(player_command, game_state):
    current_location_description = get_location_description(game_state)
    prompt_message = f"""
    **Current Location:**
    {current_location_description}

    **Your Inventory:** {game_state.inventory}

    **Your Command:** {player_command}

    Respond as the Dungeon Master. Describe what happens next in the game world based on the player's command, the current location, and the world's lore.
    Be descriptive and engaging. Advance the story based on the player's actions. Aim to keep your response to around 200 words.
    """
    st.session_state.messages.append({"role": "user", "content": player_command}) # **Ensure user message is added to chat display here**
    with st.chat_message("user"): # **Explicitly display user message here**
        st.write(player_command)
    st.session_state.messages.append({"role": "user", "content": prompt_message}) # Provide context in a 'user' message for the DM
    ai_response = generate_response(st.session_state.messages, st.session_state.api_key, st.session_state.api_provider, st.session_state.temperature)
    return ai_response

def add_item_to_inventory(item_name, game_state):
    if item_name in game_state.inventory:
        game_state.inventory[item_name] += 1
    else:
        game_state.inventory[item_name] = 1

def remove_item_from_inventory(item_name, game_state):
    if item_name in game_state.inventory and game_state.inventory[item_name] > 0:
        game_state.inventory[item_name] -= 1
        if game_state.inventory[item_name] == 0:
            del game_state.inventory[item_name]

def check_inventory(game_state):
    inventory_str = "Your Inventory:\n"
    if not game_state.inventory:
        inventory_str += "Empty"
    else:
        for item, count in game_state.inventory.items():
            inventory_str += f"- {item}: {count}\n"
    return inventory_str


# --- Streamlit UI ---
st.set_page_config(page_title="AI RPG Game", layout="wide")

# Add a full-width header image
st.image(
    "https://raw.githubusercontent.com/thecraigd/rpg-streamlit/main/AURORA_NEXUS.png",
    use_column_width=True,
)

# Display logo/title
st.title("Aurora Nexus RPG")
st.markdown("Welcome to the Aurora Nexus! A text-based AI RPG.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    api_provider = st.selectbox("API Provider", ["Deepseek Chat"])  # For now, just Deepseek
    # API Key Input Removed from Sidebar
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1, help="Controls randomness of AI responses.")

    if st.button("Start New Game"):
        if 'world_data' in st.session_state:
            start_game(st.session_state.world_data)
            st.session_state.messages = st.session_state.messages # Force re-render of chat

    st.session_state.api_provider = api_provider # Update session state with sidebar values
    st.session_state.temperature = temperature

# --- API Key from Streamlit Secrets ---
st.session_state.api_key = st.secrets.get("DEEPSEEK_API_KEY") # Access API key from secrets

# Initialize game state if not already in session
if "world_data" not in st.session_state:
    world_data = load_world_data("https://raw.githubusercontent.com/thecraigd/rpg-streamlit/main/aurora_nexus_world.json")
    st.session_state.world_data = world_data
    start_game(world_data)


# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system": # Don't show system messages directly to the user
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
if prompt := st.chat_input("Enter your command here..."):
    ai_response = handle_player_input(prompt, st.session_state)
    if ai_response:
        with st.chat_message("assistant"):
            st.write(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})


# --- Example Inventory Interaction (for testing) ---
if st.sidebar.checkbox("Show Inventory Functions (Debug)"):
    st.sidebar.subheader("Inventory (Debug)")
    item_to_add = st.sidebar.text_input("Add Item:")
    if st.sidebar.button("Add Item to Inventory"):
        add_item_to_inventory(item_to_add, st.session_state)

    item_to_remove = st.sidebar.text_input("Remove Item:")
    if st.sidebar.button("Remove Item from Inventory"):
        remove_item_from_inventory(item_to_remove, st.session_state)

    if st.sidebar.button("Check Inventory"):
        st.sidebar.write(check_inventory(st.session_state))