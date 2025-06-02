# AI-Powered E-commerce Project

## Overview

This project is an AI-powered e-commerce application that enables users to search for products using natural language queries. The system leverages large language models to understand user intent and deliver relevant product results.

## Features

- Natural language product search
- Product browsing and details
- Shopping cart functionality
- Search history tracking
- Responsive design for all devices

## Architecture

The project consists of:

- **Frontend**: React application with TypeScript, Material UI
- **Backend**: FastAPI server with MongoDB for data storage
- **AI Integration**: Integration with language models for search capabilities

### AI Workflow Architecture

Our application implements a sophisticated AI-powered search pipeline:

1. **Context Gathering**:
   - The system collects user context including search history and current cart contents
   - This contextual information helps personalize search results

2. **Query Understanding & Refinement**:
   - Raw natural language queries (e.g., "smartphone with good camera under $1000") are processed by a Language Model
   - The LLM extracts structured information including:
     - Descriptive category phrases that capture the essence of what the user wants
     - Specific filter criteria like price ranges, brands, and key product attributes
     - Tags relevant to the search
     - A concise summary of user intent

3. **Semantic Category Matching**:
   - The system converts descriptive phrases into embeddings (vector representations)
   - These embeddings are matched against a Pinecone vector database of product categories
   - This enables matching products even when users don't use exact category names

4. **Multi-stage Database Retrieval**:
   - Using matched categories and extracted filters, the system queries MongoDB
   - A sophisticated progressive fallback strategy ensures results even if initial queries return nothing:
     - First tries with all filters including text search
     - Falls back to simpler queries if needed
     - Eventually can default to category-only search

5. **Intelligent Re-ranking**:
   - Candidate products are passed to the LLM for evaluation against the original query
   - The LLM considers user context, query intent, and product details
   - Products are ranked by relevance to the user's needs
   - For each recommended product, the LLM generates a personalized justification explaining why it matches

6. **Response Generation**:
   - The final ranked products are returned with justifications
   - An overall summary explains the recommendation logic
   - Search interactions are logged for future personalization

7. **Error Handling & Resilience**:
   - Comprehensive error handling ensures graceful degradation
   - Multi-level fallback strategies guarantee users always receive results
   - Detailed logging and tracing support debugging and improvement

This advanced AI workflow combines vector search, traditional database queries, and large language models to create a truly intelligent shopping experience that understands natural human language and intent.

## Prerequisites

- Node.js (v14+)
- Python (3.8+)
- MongoDB
- pip and npm package managers

## Setup Instructions

### Quick Setup

Run the setup script to automatically set up the entire project:

```bash
./setup.sh
```

### Manual Setup

#### Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Use the search bar to search for products using natural language
3. Browse products, view details, and add items to your cart
4. Check your search history in the History page

## Technologies Used

- **Frontend**: React, TypeScript, Material UI, React Router
- **Backend**: FastAPI, PyMongo, date-fns
- **Database**: MongoDB
- **AI Components**: 
  - Large Language Models for query understanding and product ranking
  - Vector embeddings for semantic search
  - Pinecone for vector database storage
  - LangSmith for LLM observability and tracing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
