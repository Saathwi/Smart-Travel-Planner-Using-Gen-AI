**Smart Travel Planner using Generative AI**

An AI-powered application to create personalized, dynamic travel
itineraries based on user preferences, real-time data, and natural
language interaction.

**Dataset Loading Steps**

-   The Smart Travel Planner utilizes a Kaggle dataset containing
    airport names, IATA codes, and related information to extract city
    names, airport codes, and airport names. This data is used for
    flight searches and destination plotting on Folium maps.

-   Additionally, it dynamically gathers real-time information through:
    -   Web scraping (using BeautifulSoup) for hotel and flight details.
    -   Public APIs and Hugging Face models for AI-driven itinerary
    generation.

**Installation and Execution Process:**

Follow these steps to install and set up the Smart Travel Planner
project:

1.  **Download and extract the project folder**

    -   Download the project folder from the provided drive link.

    -   Extract it if it is zipped.

2.  **Navigate to the project directory**

    -   Open a terminal or command prompt and move into the project
        folder:

        > cd smart-travel-planner

3.  **Create a virtual environment** (optional but recommended):

    > python -m venv venv

4.  **Activate the virtual environment**:

    -   On **Windows**:

    > venv\\Scripts\\activate

-   On **Mac/Linux**:

    >source venv/bin/activate

5.  **Install all required Python libraries** from the requirements.txt
    file:

    > pip install -r requirements.txt

6.  **Generate the Airport Mapping File** (needed for flights and city
    names):

    > python flight_names.py

-   This will create a airport_mapping.json file inside the project
    folder.

7.  **Obtain and Configure Hugging Face Token**

-   Get model access:

    -   Visit
        [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
        on Hugging Face.

    -   Request access if required and wait for approval.

-   Create a new Access Token:

    -   Go to your Hugging Face account settings → **Access Tokens**.

    -   Click **New Token**, set **Read** permissions, and **generate**
        the token.

    -   Copy the token securely.

-   Login via Terminal:

    -   Open your terminal and enter: 
        >huggingface-cli login

    -   Paste the copied Hugging Face token when prompted

8.  **Run the Streamlit Application**:

    > streamlit run app.py

9.  **Access the application**:

    -   After running the command, the application will automatically
        open in your browser at:

        > http://localhost:8501

**Important Notes**

-   Python Version:\
    Ensure you have Python 3.9 or higher installed on your system.

-   Internet Connection Required:\
    The application fetches real-time flight, hotel, and itinerary data.
    Keep your device connected to the internet while running the
    project.

-   Run flight_names.py First:\
    Always run flight_names.py before starting the app to generate the
    airport_mapping.json file necessary for flight and destination
    searches.

-   Hugging Face Token Setup:

    -   Make sure you have created and logged in with your Hugging Face
        Read access token using huggingface-cli login.

    -   Access to the Mistral-7B-Instruct-v0.2 model must be granted
        beforehand from Hugging Face.

-   Virtual Environment (Recommended):\
    Use a virtual environment to avoid dependency conflicts with other
    Python projects.

-   Browser Compatibility:\
    The application is best accessed using Google Chrome or Microsoft
    Edge.

-   Folder Structure:\
    Keep all project files in their original folders (like /scraper/,
    /ai_utils/, /auth/) without renaming or moving them, to ensure
    smooth execution.

-   Common Errors:

    -   If streamlit or huggingface_hub command not found → Install
        using 
        >pip install streamlit huggingface_hub

    -   If ModuleNotFoundError → Double-check that all libraries from
        requirements.txt are properly installed.
