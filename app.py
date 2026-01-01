# Import the necessary modules
import streamlit as st
import json
import requests
from openai import OpenAI 
import google.generativeai as genai
from google.generativeai import types as genai_types
from PIL import Image
from io import BytesIO
import base64

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
        if provider == "Google Gemini Flash 2.0 Experimental":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3-flash-preview")

            # Convert message history to text format
            conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = model.generate_content(conversation) # Gemini API does not have explicit temperature parameter here.

            return response.text

        elif provider == "Deepseek Chat":
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature, # Use the temperature parameter
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

# --- NEW: Image Generation Function ---
def generate_image(text_prompt, api_key):
    if not api_key:
        if st.session_state.get('debug_mode', False):
            st.sidebar.write("Debug: API key not configured")
        return None, "API key not configured."
    
    try:
        # Make sure the API is properly configured with the key
        genai.configure(api_key=api_key)
        
        # Create an extremely generic, abstract prompt with no references to specific content
        # This is our last attempt to avoid policy violations
        image_prompt = "Create an abstract futuristic landscape with stars and technology. Completely fictional, no text, no characters."
        
        if st.session_state.get('debug_mode', False):
            st.sidebar.write(f"Debug: Using ultra-generic prompt: '{image_prompt}'")
        
        # Use the simplest possible approach
        model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
        response = model.generate_content(image_prompt)
        
        if st.session_state.get('debug_mode', False):
            st.sidebar.write("Debug: Response received")
        
        # Check if we got an error or policy violation
        if hasattr(response, 'text') and response.text:
            if "violates" in response.text.lower() or "policy" in response.text.lower():
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write(f"Debug: Policy violation: {response.text[:100]}...")
                
                # If we're getting policy violations even with the most generic prompt,
                # the feature may not be available for this API key or account
                return None, "Image generation not currently available"
            
            # If the response is just text but not an error, we still don't have an image
            if len(response.text) > 100:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write(f"Debug: Got text response instead of image: {response.text[:100]}...")
                return None, "Image generation returned text instead of an image"
        
        # Try to extract image data if present
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                # Check for inline_data (image)
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    try:
                        image_bytes = BytesIO(base64.b64decode(part.inline_data.data))
                        image = Image.open(image_bytes)
                        if st.session_state.get('debug_mode', False):
                            st.sidebar.write(f"Debug: Successfully parsed image: {image.format} {image.size}")
                        return image, "Generated scene image"
                    except Exception as img_e:
                        if st.session_state.get('debug_mode', False):
                            st.sidebar.write(f"Debug: Failed to process image data: {str(img_e)}")
        
        # If we got here, we couldn't extract an image
        if st.session_state.get('debug_mode', False):
            st.sidebar.write("Debug: No image found in the response")
        
        # At this point, we should consider the image generation feature unavailable
        # and recommend disabling it to avoid further policy violations
        return None, "Scene visualization unavailable (recommend disabling images in settings)"
    
    except Exception as e:
        error_msg = f"Error in image generation: {str(e)}"
        if st.session_state.get('debug_mode', False):
            st.sidebar.write(f"Debug: {error_msg}")
        return None, error_msg

# --- Game Logic Functions ---
def start_game(world_data):
    st.session_state.world_data = world_data
    st.session_state.inventory = {}
    st.session_state.current_station = "New Eden"  # Example starting station
    st.session_state.current_town = "Cygnus Enclave"  # Example starting town

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
    Give some context of the whole Aurora Nexus with its many stations and abundance of variety. Describe the player's immediate surroundings in {st.session_state.current_town} and wait for their first command. 
    Keep your descriptions evocative and engaging, setting the scene for an immersive role-playing experience.
    Remember to act as the Dungeon Master and guide the player through the world. Aim to keep your initial description to around 250 words.
    """

    initial_messages = [
        {"role": "system", "content": "You are a Dungeon Master for a text-based RPG. Use the provided world data to describe locations, NPCs, and events. Be creative and engaging. Keep responses concise, aiming for approximately 150 words or less."},
        {"role": "user", "content": initial_prompt_content} # Send the initial prompt as a user message to trigger the DM response
    ]

    initial_response = generate_response(initial_messages, st.session_state.api_key, st.session_state.api_provider, st.session_state.temperature)

    # Generate an image for the initial scene if images are enabled
    if st.session_state.get('enable_images', True) and initial_response and not initial_response.startswith("API key not configured"):
        try:
            if st.session_state.get('debug_mode', False):
                st.sidebar.write("Debug: Attempting to generate initial scene image...")
                
            image_data, image_caption = generate_image(initial_response, st.session_state.api_key)
            
            if image_data:
                st.session_state.current_image = image_data
                st.session_state.current_image_caption = image_caption
                
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write("Debug: Initial scene image successfully generated")
            else:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write(f"Debug: Failed to generate initial image. Reason: {image_caption}")
                st.session_state.current_image = None
                st.session_state.current_image_caption = None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.write(f"Debug: Exception during initial image generation: {str(e)}")
            st.session_state.current_image = None
            st.session_state.current_image_caption = None
    else:
        st.session_state.current_image = None
        st.session_state.current_image_caption = None

    st.session_state.messages = [
        {"role": "system", "content": "You are a Dungeon Master for a text-based RPG. Use the provided world data to describe locations, NPCs, and events. Be creative and engaging. Keep responses concise, aiming for approximately 150 words or less."},
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
    Be descriptive and engaging. Advance the story based on the player's actions. Aim to keep your response to around 150 words or less.
    """
    st.session_state.messages.append({"role": "user", "content": player_command}) # Keep this line to display the player's command
    with st.chat_message("user"): # **Explicitly display user message here**
        st.write(player_command)
    
    # Generate the AI response
    ai_response = generate_response(st.session_state.messages + [{"role": "user", "content": prompt_message}], st.session_state.api_key, st.session_state.api_provider, st.session_state.temperature)
    
    # Generate image for the new scene if images are enabled
    if st.session_state.get('enable_images', True):
        try:
            if st.session_state.get('debug_mode', False):
                st.sidebar.write("Debug: Attempting to generate image...")
                
            image_data, image_caption = generate_image(ai_response, st.session_state.api_key)
            
            if image_data:
                st.session_state.current_image = image_data
                st.session_state.current_image_caption = image_caption
                
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write("Debug: Image successfully generated")
            else:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.write(f"Debug: Failed to generate image. Reason: {image_caption}")
                st.session_state.current_image = None
                st.session_state.current_image_caption = None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.write(f"Debug: Exception during image generation: {str(e)}")
            st.session_state.current_image = None
            st.session_state.current_image_caption = None
    
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
st.set_page_config(
    page_title="AURORA NEXUS - AI RPG Game",
    layout="wide",
    initial_sidebar_state="collapsed"  # Set to "collapsed" to minimize the sidebar
)

# Inject custom CSS for styling
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background-color: black;
        color: white;
    }

    /* Sidebar background */
    .css-1d391kg {
        background-color: black;
        color: white;
    }

    /* Sidebar text */
    .css-1v3fvcr {
        color: white;
    }
    
    /* Input boxes and sliders */
    .css-1d0tddn, .css-1n76uvr {
        background-color: #333333; /* Dark gray for input boxes */
        color: white;
    }

    /* Chat messages */
    .stMarkdown > div, .st-chat-message {
        background-color: #222222;
        color: white;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* Adjust input text box */
    textarea, input {
        background-color: #333333;
        color: white;
    }

    /* Scene Image container */
    .scene-image-container {
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Scene Image */
    .scene-image {
        border-radius: 10px;
        border: 1px solid #444;
        max-width: 100%;
    }

    </style>
    """,
    unsafe_allow_html=True
)

temperature = 0.7

# Add a full-width header image
st.image(
    "https://raw.githubusercontent.com/thecraigd/rpg-streamlit/main/AURORA_NEXUS.png",
    use_container_width=True,
)

# Display logo/title
# st.title("Aurora Nexus RPG") # removed and replaced with header image
st.markdown("""Welcome to the Aurora Nexus! A text-based AI RPG.

The Aurora Nexus uses modern Large language Model technology to power a fully interactive RPG where you can explore a complete sci-fi environment. Each playthrough is unique, and with a wide array of unique space stations to explore and characters to meet, the possibilites are endless!

Thanks for your patience while the first part of your adventure is created...""")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    api_provider = st.selectbox("API Provider", ["Google Gemini Flash 3", "Deepseek Chat"])  
    
    # Image generation toggle with warning
    st.markdown("**Scene Visualization**")
    enable_images = st.checkbox("Enable Scene Images", value=False)  # Default to OFF for now
    
    if enable_images:
        st.info("Note: Image generation is experimental and may not be available with all API keys. If you see policy violation messages, try disabling this feature.")
    
    # Add debug mode toggle
    debug_mode = st.checkbox("Debug Mode", value=False)
    
    if st.button("Start New Game"):
        if 'world_data' in st.session_state:
            start_game(st.session_state.world_data)
            st.session_state.messages = st.session_state.messages # Force re-render of chat

    st.session_state.api_provider = api_provider # Update session state with sidebar values
    st.session_state.temperature = temperature
    st.session_state.enable_images = enable_images
    st.session_state.debug_mode = debug_mode

# --- API Key from Streamlit Secrets ---
if api_provider == "Deepseek Chat":
    st.session_state.api_key = st.secrets.get("DEEPSEEK_API_KEY") # Access API key from secrets
else:
    st.session_state.api_key = st.secrets.get("GOOGLE_API_KEY") # Access API key from secrets

# Initialize game state if not already in session
if "world_data" not in st.session_state:
    world_data = load_world_data("https://raw.githubusercontent.com/thecraigd/rpg-streamlit/main/aurora_nexus_world.json")
    st.session_state.world_data = world_data
    start_game(world_data)

# Initialize messages if not already in session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a Dungeon Master for a text-based RPG. Use the provided world data to describe locations, NPCs, and events. Be creative and engaging. Keep responses concise, aiming for approximately 150 words or less."},
        {"role": "assistant", "content": "Welcome to Aurora Nexus! I'll be your guide through this adventure. Type a command to begin."}
    ]

# Display chat messages
if "messages" in st.session_state:
    for message in st.session_state.messages:
        if message["role"] != "system": # Don't show system messages directly to the user
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Display current scene image after assistant messages
                if message["role"] == "assistant" and 'current_image' in st.session_state and st.session_state.current_image is not None and st.session_state.get('enable_images', True):
                    try:
                        st.image(st.session_state.current_image, 
                                 caption=st.session_state.get('current_image_caption', 'Scene illustration'), 
                                 use_column_width=True)
                    except Exception as e:
                        st.error(f"Failed to display image: {str(e)}")
                        if st.session_state.get('debug_mode', False):
                            st.sidebar.write(f"Debug: Image display error: {str(e)}")
                            st.sidebar.write(f"Debug: Image type: {type(st.session_state.current_image)}")

# Chat input
if prompt := st.chat_input("Enter your command here..."):
    ai_response = handle_player_input(prompt, st.session_state)
    if ai_response:
        with st.chat_message("assistant"):
            st.write(ai_response)
            
            # Display the generated image
            if 'current_image' in st.session_state and st.session_state.current_image is not None and st.session_state.get('enable_images', True):
                try:
                    st.image(st.session_state.current_image, 
                             caption=st.session_state.get('current_image_caption', 'Scene illustration'), 
                             use_column_width=True)
                except Exception as e:
                    st.error(f"Failed to display image: {str(e)}")
                    st.sidebar.write(f"Debug: Image display error: {str(e)}")
                    st.sidebar.write(f"Debug: Image type: {type(st.session_state.current_image)}")
            
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