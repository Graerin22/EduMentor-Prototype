### Prerequisites
Make sure you have Python 3.10+ installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/Graerin22/EduMentor-Prototype.git
cd EduMentor-Prototype
```

### 2. Set Up Your Gemini API Key
This project requires a Gemini API key to power the AI features. Getting a key is **free and takes less than a minute**:

1. Go to https://aistudio.google.com/
2. Log in with any Google account.
3. Click the **"Get API key"** button at the top left.
4. Click **"Create API key"**, select your project or create a new one, and copy the generated key.

### 3. Configure Environment Variables
1. Look at the root directory of this project and locate the `.env.example` file.
2. Duplicate or rename this file to exactly `.env`.
3. Open the `.env` file in your text editor and paste your copied API key after the `=` sign:

```text
GEMINI_API_KEY=paste_your_actual_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Install Dependencies & Run
Set up your virtual environment, install the required packages, and launch the application:

```bash
# Windows
python -m venv myappenv
myappenv\Scripts\activate

# macOS/Linux
python3 -m venv myappenv
source myappenv/bin/activate

# Install requirements and run
pip install -r requirements.txt
python main.py
```
