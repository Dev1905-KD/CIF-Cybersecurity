CIF SINGLE-PAGE INTERFACE — SETUP

1. Extract the frontend folder into your CIF-Cybersecurity repository.
   The repository should contain:
     CIF-Cybersecurity/
       api/main.py
       frontend/
       rag/
       agents/
       ...

2. Copy api/main.py into a new api folder at the repository root.

3. In the repository root, activate your existing virtual environment:
     .\venv\Scripts\Activate.ps1

4. Install backend packages if needed:
     pip install fastapi uvicorn

5. Start the API from the repository ROOT (not from api/):
     python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

6. In a SECOND PowerShell terminal:
     cd frontend
     npm install
     npm run dev

7. Open:
     http://127.0.0.1:5173

8. Check API:
     http://127.0.0.1:8000/api/health

IMPORTANT:
- Keep the Python API terminal open while using the frontend.
- The first investigation may take time while Ollama/Neo4j are contacted.
- Do not start multiple API processes simultaneously; this starter keeps one pipeline
  instance alive for the server lifetime.
- The API wrapper calls your existing CRAGLlamaPipeline.run(query). It does not
  change retrieval, verification, belief, simulation, or decision logic.
- If your local branch has different import paths, share the terminal traceback
  rather than changing the pipeline imports blindly.
