# 1-CapstoneProject 'Chat With Data'

A Streamlit-based AI chatbot application that allows users to interact with a wine database using natural language queries. The application uses OpenAI's API to interpret user questions and convert them into SQL queries to retrieve information about wines from different categories (Red, White, Rosé, and Sparkling wines).

## Features

- 🍷 **Interactive Chat Interface**: Natural language queries about wine data
- 📊 **Real-time Database Statistics**: View wine collection metrics in the sidebar
- 🤖 **AI-Powered SQL Generation**: Automatic conversion of questions to safe SQL queries
- 🔒 **Safe Database Access**: Read-only queries with built-in security measures
- 🎫 **GitHub Integration**: Automatic support ticket creation for technical issues
- 🌍 **Comprehensive Wine Data**: Information from multiple countries and regions

## Prerequisites

Before running this project, ensure you have:

- Python 3.9 or higher
- MySQL server running locally or accessible remotely
- OpenAI API key
- GitHub personal access token (optional, for support ticket feature)

# HOW TO RUN THE PROJECT

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd GenAiCourse/capstone_i
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Environment Setup

Create a `.env` file in the `capstone_i` directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4o-mini

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/wine

# GitHub Integration (Optional)
GITHUB_TOKEN=your_github_personal_access_token
REPO=your_username/your_repository_name
```

## Database Setup

1. **Install and start MySQL server**

   - Make sure MySQL is running on your system
   - Create a database named `wine`

2. **Import the wine database**

   ```bash
   mysql -u your_username -p wine < dump_for_restore.sql
   ```

3. **Verify the database setup**
   - The database should contain tables: `red`, `white`, `rose`, `sparkling`, and `varieties`
   - Each table contains wine information with columns like Name, Country, Region, Winery, Rating, etc.

## Running the Application

1. **Start the Streamlit application**

   ```bash
   streamlit run app.py
   ```

2. **Access the application**
   - Open your web browser and navigate to `http://localhost:8501`
   - The application will display database statistics in the sidebar
   - Use the chat interface to ask questions about wines

## Usage Examples

Try asking questions like:

- "Show me the top 5 highest rated red wines"
- "What are the most expensive wines from France?"
- "Which countries produce the most rosé wines?"
- "Find wines with a rating above 4.5 from Italy"
- "What's the average price of sparkling wines?"

![Usage](/docs/images/usage.png)

![Support](/docs/images/github_support.png)

Data Provided by [Wine Rating & Price](https://www.kaggle.com/datasets/budnyak/wine-rating-and-price)

## Dataset columns

Below are the columns for each wine category (parsed from the provided data):

### Red

| Column          | Type | Null |
| --------------- | ---- | :--: |
| Name            | text | YES  |
| Country         | text | YES  |
| Region          | text | YES  |
| Winery          | text | YES  |
| Rating          | text | YES  |
| NumberOfRatings | text | YES  |
| Price           | text | YES  |
| Year            | text | YES  |

### Rose

| Column          | Type   | Null |
| --------------- | ------ | :--: |
| Name            | text   | YES  |
| Country         | text   | YES  |
| Region          | text   | YES  |
| Winery          | text   | YES  |
| Rating          | double | YES  |
| NumberOfRatings | int    | YES  |
| Price           | double | YES  |
| Year            | text   | YES  |

### Sparkling

| Column          | Type | Null |
| --------------- | ---- | :--: |
| Name            | text | YES  |
| Country         | text | YES  |
| Region          | text | YES  |
| Winery          | text | YES  |
| Rating          | text | YES  |
| NumberOfRatings | text | YES  |
| Price           | text | YES  |
| Year            | text | YES  |

### Varieties

| Column | Type | Null |
| ------ | ---- | :--: |
| C1     | text | YES  |

### White

| Column          | Type | Null |
| --------------- | ---- | :--: |
| Name            | text | YES  |
| Country         | text | YES  |
| Region          | text | YES  |
| Winery          | text | YES  |
| Rating          | text | YES  |
| NumberOfRatings | text | YES  |
| Price           | text | YES  |
| Year            | text | YES  |
