FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir hatchling && pip install --no-cache-dir -e .

COPY . .

# Default: run baseline with random agent (no API key needed)
# Override: docker run -e OPENAI_API_KEY=sk-... image python scripts/baseline.py --agent llm
CMD ["python", "scripts/baseline.py", "--agent", "random"]
