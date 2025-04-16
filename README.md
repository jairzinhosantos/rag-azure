# RAG-AZURE

## Contents
[Project Overview](#mag-project-overview)<br>
[Components](#open_file_folder-components)<br>
[Tools Used](#hammer_and_wrench-tools-used)<br>
[Getting Started](#rocket-getting-started)<br>
[Configuration](#gear-configuration)<br>
[Agile Development Benefits](#fast_forward-agile-development-benefits)<br>
[Contributing](#handshake-contributing)<br>
[License](#page_facing_up-license)<br>

# RAG-AZURE :robot:

**`A modular and scalable Retrieval-Augmented Generation (RAG) solution built with Azure services, designed for rapid MVP development and validation of RAG implementations.`**

## :mag: Project Overview

RAG-AZURE is a well-structured project that implements a RAG (Retrieval-Augmented Generation) system using Azure services. The project follows a modular architecture that enables quick development, testing, and deployment of RAG solutions, leveraging services like Azure OpenAI, Azure AI Search, and Azure Cosmos DB.

## :open_file_folder: Components

Below is a breakdown of the key components included in this repository:

- **`app.py`**: Main Flask application entry point. Handles HTTP requests, routing, and user sessions.
- **`orchestrator.py`**: Core orchestration logic. Coordinates Azure services, manages conversation flow, context, and cost tracking.
- **`services/`**: Contains clients for interacting with Azure services.
  - [`azopenai.py`](services/azopenai.py): Manages interactions with the Azure OpenAI service.
  - [`aisearch.py`](services/aisearch.py): Handles vector search and document retrieval using Azure AI Search.
  - [`cosmosdb.py`](services/cosmosdb.py): Manages conversation history and evaluation metrics storage in Azure Cosmos DB.
- **`config/`**: Configuration files.
  - [`config.json`](config/config.json): JSON file containing parameters for Azure services, models, prompts, etc.
  - [`config.py`](config/config.py): Python script to load the configuration.
- **`static/`**: Static web assets (CSS, JavaScript, images).
- **`templates/`**: HTML templates for the Flask application (e.g., `index.html`).
- **`prompts/`**: Stores system and potentially user prompts used by the RAG model.
- **`tools_functions/`**: Likely contains definitions for custom tools or functions callable by the language model (if used).
- **`requirements.txt`**: Lists Python dependencies for the project.
- **`.env`**: Environment file for storing secrets like API keys and connection strings.
- **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.
- **`README.md`**: This file, providing a detailed description of the project.

## :hammer_and_wrench: Tools Used

The following key technologies and services are utilized in this project:

1.  **Flask**: Micro web framework for the application layer.
2.  **Azure OpenAI**: Provides access to powerful language models (like GPT-4o).
3.  **Azure AI Search**: Used for efficient retrieval of relevant document chunks.
4.  **Azure Cosmos DB**: NoSQL database for storing chat history and evaluation data.
5.  **Python**: The primary programming language.
6.  **Asyncio**: For handling asynchronous operations, improving performance.

## :rocket: Getting Started

Follow these steps to set up and run the project on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url> # Replace with your repo URL
    cd RAG-AZURE
    ```
2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Azure Services:**
    *   Fill in your Azure service details (endpoints, keys, deployment names) in `config/config.json`.
    *   Create a `.env` file in the root directory and add necessary environment variables (e.g., `FLASK_SECRET_KEY`, potentially Azure credentials if not in `config.json`). Refer to `.env.example` if provided, or the configuration loader (`config.py`) for required variables.
5.  **Run the application:**
    ```bash
    python app.py
    ```

## :gear: Configuration

The `config/config.json` file is central to the project's configuration. It contains settings for:
- Azure service connection details (Endpoints, API Keys - *though keys are often better in `.env`*).
- Azure OpenAI model deployment names and parameters.
- Azure AI Search index details.
- Azure Cosmos DB database and container names.
- Paths to prompts, tools, and function definitions.
- Flask application settings (host, port).

## :fast_forward: Agile Development Benefits

This project structure offers several advantages for agile development:

1.  **Modularity**: Clear separation between the web app, orchestration logic, and individual Azure service interactions allows for independent development, testing, and updates.
2.  **Rapid Development**: Pre-built clients for Azure services and a standardized configuration system accelerate the setup and integration process.
3.  **Easy Validation**: Storing chat history and evaluation metrics (like token counts and costs) in Cosmos DB facilitates analysis and validation of the RAG system's performance and efficiency.
4.  **Scalability**: Using async operations and distinct service modules makes it easier to scale components independently.
5.  **Maintainability**: A clear, organized structure with separated concerns simplifies debugging and future enhancements.

## :handshake: Contributing

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

## :page_facing_up: License

This project is licensed under the MIT License - see the LICENSE file for details (assuming an MIT license). 