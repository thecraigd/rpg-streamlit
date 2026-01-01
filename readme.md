[![CraigDoesData][logo]][link]

[logo]: https://github.com/thecraigd/Python_SQL/raw/master/img/logo.png
[link]: https://www.craigdoesdata.com/

[image]: https://github.com/thecraigd/rpg-streamlit/blob/main/AURORA_NEXUS.png?raw=true
[imglink]: https://www.craigdoesdata.com/rpg

# Aurora Nexus AI RPG - Your Text-Based Adventure

[![Aurora_Nexus][image]][imglink]

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://www.craigdoesdata.com/rpg)

Welcome to **Aurora Nexus AI RPG**, an immersive text-based role-playing game powered by cutting-edge AI and brought to life with [Streamlit](https://streamlit.io/).  This application transforms your web browser into a dynamic and ever-evolving game world, ready for you to explore and shape with your choices.

## What is Aurora Nexus?

Aurora Nexus is an engaging RPG experience where you take on the role of an adventurer in a rich, AI-generated sci-fi universe.  Using powerful language models, the game dynamically responds to your commands, weaving a narrative tailored to your actions.  Imagine a classic text-based adventure, but with a Dungeon Master that's always ready to surprise you with fresh content and unexpected turns.

**Key Features:**

*   **AI-Powered Dungeon Master:**  Experience a dynamic and responsive game master that reacts to your choices and guides you through the world.
*   **Endless Possibilities:**  Explore a vast sci-fi universe with unique locations, characters, and storylines that unfold based on your interactions.
*   **Streamlit Interface:**  Enjoy a clean and user-friendly web interface for seamless gameplay directly in your browser.
*   **Multiple AI Provider Support:** Choose between different AI providers (like Google Gemini and Deepseek Chat) to power your game, offering flexibility and potentially different narrative styles (API keys required - see Configuration).
*   **Customizable World:**  The game is currently pre-loaded with the "Aurora Nexus" world, but the architecture is designed to support different world data in the future.
*   **Inventory System (WIP):** Manage your items and resources as you journey through the game world, adding another layer of strategic gameplay.

## Getting Started

Ready to embark on your adventure? Here's how to get Aurora Nexus running:

### Prerequisites

*   **Python 3.8+:** Make sure you have Python installed on your system.
*   **Streamlit:** Install Streamlit if you haven't already:
    ```bash
    pip install streamlit
    ```
*   **OpenAI Python Library:** (For Deepseek Chat) Install the OpenAI Python library:
    ```bash
    pip install openai
    ```
*   **Google Generative AI Python Library:** (For Google Gemini) Install the Google Generative AI library:
    ```bash
    pip install google-generativeai
    ```

### Installation and Running Locally

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/thecraigd/rpg-streamlit.git
    cd rpg-streamlit
    ```

2.  **API Keys:**  **Crucially, you'll need API keys to use the AI providers.**
    *   **For Deepseek Chat:** You'll need an API key from [Deepseek](https://platform.deepseek.com/).
    *   **For Google Gemini:** You'll need a [Google Gemini API key](https://aistudio.google.com/apikey).

    **Set up your API keys as Streamlit secrets.**  The easiest way to do this is to create a file named `.streamlit/secrets.toml` in the root of your repository (or in your Streamlit deployment directory).  Add your API keys to this file like so, replacing `YOUR_DEEPSEEK_API_KEY` and `YOUR_GOOGLE_API_KEY` with your actual keys:

    ```toml
    DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
    ```

    If you're deploying to the Streamlit [Community Cloud](https://streamlit.io/cloud) you can add the contents of your .toml file to the Secrets for the web app, accessed via the app settings.

    **Important:**  Do not commit your `secrets.toml` file to your public repository for security reasons.  It's good practice to add `.streamlit/secrets.toml` to your `.gitignore` file.

3.  **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```

    This command will start the Streamlit application, and it will automatically open in your web browser (usually at `http://localhost:8501`).

### Configuration within the App

Once the app is running in your browser:

1.  **API Provider Selection:** In the left sidebar, you can choose your preferred **API Provider** from the dropdown menu ("Google Gemini Flash 3" or "Deepseek Chat"). The application will use the corresponding API key you've configured in your Streamlit secrets.
2.  **Start a New Game:** Click the "Start New Game" button in the sidebar to begin your adventure in the Aurora Nexus!

## Playing the Game

*   **Initial Setup:** When you start a new game, the AI Dungeon Master will introduce you to your starting location and set the scene. Read the descriptions carefully to understand your surroundings.
*   **Input Commands:** Use the chat input at the bottom of the screen to type your commands.  Tell the AI what you want to do!  For example:
    *   `"Examine the market stalls."`
    *   `"Talk to the bartender."`
    *   `"Look in my inventory."`
    *   `"Travel to the next town."` (if applicable in the game world)
*   **Engage with the World:**  The AI will respond to your commands, describing the outcomes and advancing the story.  Be creative and explore the world!
*   **Inventory (Optional Debug):**  For testing and development, there are "Inventory Functions (Debug)" in the sidebar that you can enable to manually add, remove, and check items in your inventory. In normal gameplay, inventory management will be integrated into the AI's responses based on your actions (at this time, this is a WIP, so may not function as expected!).

## Contributing

Contributions are welcome! If you have ideas for improvements, new features, world data, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or fix.
3.  Make your changes and commit them.
4.  Submit a pull request.

Let's work together to make Aurora Nexus an even more amazing AI RPG experience!

## License

This project is licensed under the MIT License.

---

**Enjoy your adventure in the Aurora Nexus!**  I hope you have a fantastic time exploring this AI-powered world.
