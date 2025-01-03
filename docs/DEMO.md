## **Features**

- Fetch emails from a Gmail account using OAuth2 authentication.
- Display email details including sender, subject, and body.
- Generate summaries of emails using OpenAI's GPT-3.5-turbo model.
- Serve email data via RESTful API endpoints using FastAPI.

## **Requirements**

- .env file with the following variables: (See Discord#resources)
  - EMAIL_ACCOUNT: The email address of the Gmail account to fetch emails from.
  - GOOGLE_CLIENT_ID: The client ID obtained from the Google API Console.
  - GOOGLE_CLIENT_SECRET: The client secret obtained from the Google API Console.
  - OPENAI_API_KEY: The API key obtained from OpenAI.

## **Installation**

1. Clone the repository:

```bash
git clone https://github.com/EmailEssence/EmailEssence.git
```

change the directory to the proto folder:

```bash
cd proto
```

2. Create a virtual environment:

I developed this project using Python 3.12.4. 
No guarantees are made that this will work with other versions of Python.

VSCode ctrl+shift+p > Python: Create Virtual Environment using /proto/requirements.txt

or

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install Dependencies:

```bash
pip install -r requirements.txt
```

4. Verify environment variables:
Important this doesn't get published to the repo.

```
EMAIL_ACCOUNT
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
OPENAI_API_KEY
```

### **Demo**

To prepare for the demo, I recommend opening a browser window and navigating to the following URLs ahead of time.

- http://127.0.0.1:8000/emails/
- http://127.0.0.1:8000/docs

#### **Procedure**

1. Run the app using the following command:

```bash
uvicorn main:app --reload
```
---
2. Open http://127.0.0.1:8000/emails/ in your browser. This will initialize the oauth flow and redirect you to the Google login page.

**Talking Points:**
- We are just beginning to learn about OAuth2 authentication, and as such this is a very basic implementation.

- We are fetching all emails from the user's Gmail account, rather than just the most recent ones in the inbox.

- We are utilizing IMAP, but oauth2 is still required by most email providers.

---

3. Open http://127.0.0.1:8000/docs in your browser. Click on the "Try it out" button for the GET /emails/ endpoint. 

**Talking Points**:
- FastAPI provides automatic documentation via Swagger UI.
- The /docs interface allows interactive testing of API endpoints. Including showing the request and response bodies along with the schema of the response.
- These endpoints are prototypes and will evolve as the project develops.

---

4. Click on the "Try it out" button for the GET /emails/summarize endpoint. This will send all emails to the OpenAI API and return a summary of each email.

**Talking Points**:
- Summarization uses OpenAI's GPT-4o-mini model.
- API usage WILL incur costs; monitoring and optimization are planned.
- Future improvements include refining the summarization prompt and exploring local LLMs.

#### **Endpoints**

- http://127.0.0.1:8000/emails/: Retrieves emails from the Gmail account.
- http://127.0.0.1:8000/emails/summarize: Generates summaries of the emails using OpenAI's API.