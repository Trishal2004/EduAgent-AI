# 🎓 EduAgent AI — Intelligent Learning Assistant

**EduAgent AI** is an AI-powered learning platform designed to help students learn smarter, organize study materials, and prepare for examinations efficiently. It brings AI-assisted learning tools into one place, making it easier to understand concepts, generate study notes, practice questions, and interact with learning documents.

## ✨ Key Features

- 🤖 **AI Tutor** — Get explanations, answers, and guidance on academic topics.
- 📝 **Smart Study Notes** — Generate detailed, structured notes with definitions, explanations, examples, and key points.
- 📚 **Document Management** — Upload, organize, and access study documents.
- 🧠 **AI-Powered Document Q&A** — Ask questions about learning materials and retrieve relevant information using Retrieval-Augmented Generation (RAG).
- 🗂️ **Flashcards** — Create study decks for revision and active recall.
- 📝 **Quizzes and Practice** — Test your knowledge and reinforce concepts through practice questions.
- 📄 **Question Paper Support** — Organize and work with examination-oriented study materials.
- 📖 **Collections** — Keep related notes and resources organized for easier access.

## 🎯 Project Objective

The goal of EduAgent AI is to make learning more personalized, interactive, and accessible. Instead of switching between multiple study tools, students can use a unified platform to explore concepts, manage educational resources, revise important topics, and prepare for exams.

## 🛠️ Technology Stack

The project uses a Python-based backend and a web frontend. The exact technologies may vary by module.

- **Backend:** Python, FastAPI
- **Database:** SQLite (current development configuration)
- **AI Integration:** Google Gemini / Google GenAI SDK
- **AI and Retrieval:** Retrieval-Augmented Generation (RAG), embeddings, and vector search
- **Vector Database:** Qdrant, where configured
- **Frontend:** React and JavaScript, where used
- **Version Control:** Git and GitHub

## 🚀 Getting Started

### Prerequisites

Install the following tools before running the project:

- Python 3.10 or a version supported by the project dependencies
- Node.js and npm, if the frontend uses React
- Git
- A Google Gemini API key for AI features that require it
- Docker, if running Qdrant through Docker

### 1. Clone the Repository

```bash
git clone https://github.com/Trishal2004/EduAgent-AI.git
cd EduAgent-AI
```

### 2. Set Up the Backend

Navigate to the backend directory containing the Python application and its dependency file.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create or update the `.env` file using the environment variables required by the application. For example:

```env
DATABASE_URL=sqlite:///./eduagent.db
GOOGLE_API_KEY=your_google_gemini_api_key
```

Use the exact variable names expected by your application configuration. Never commit API keys or other secrets to GitHub.

### 3. Run the Backend

If the FastAPI application entry point is `app.main:app`, start the server with:

```bash
uvicorn app.main:app --reload
```

Open the API documentation in your browser:

```text
http://127.0.0.1:8000/docs
```

### 4. Set Up the Frontend

If the frontend is in a separate directory, open another terminal and navigate to it:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by the frontend development server.

> **Note:** Adjust the directory names and commands to match the actual repository structure and `package.json` scripts.

## 🔐 Environment Variables

Store credentials and configuration in a local `.env` file. Configure only the variables required by your application, such as:

- Google Gemini API credentials
- Database connection settings
- Vector database connection settings, if applicable

Ensure `.env`, API keys, and other sensitive files are excluded from version control.

## 📂 Project Modules

EduAgent AI is designed around the following learning modules:

| Module | Purpose |
|---|---|
| AI Tutor | Interactive academic assistance |
| Study Notes | Detailed topic-based notes |
| Flashcards | Revision and active recall |
| Documents | Study material uploads and management |
| Collections | Organized learning resources |
| Practice | Topic-based question practice |
| Quiz | Knowledge assessment |
| Question Papers | Examination preparation |

## 🔮 Future Enhancements

- Personalized learning recommendations
- Progress tracking and performance analytics
- Improved document-grounded answers with citations
- Exportable study notes and revision materials
- Voice-based interaction and accessibility improvements
- Automated study plans and revision schedules

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome. If you would like to improve EduAgent AI, fork the repository, create a feature branch, and submit a pull request.

## 👨‍💻 Author

**Trishal**

GitHub: [@Trishal2004](https://github.com/Trishal2004)

## 📄 License

A license has not yet been specified. Add a `LICENSE` file and update this section when you decide how the project may be used and distributed.

---

⭐ If you find EduAgent AI useful, consider starring the repository!

