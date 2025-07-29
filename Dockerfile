# Use Python slim image
FROM python:3.9-slim

WORKDIR /app

# Upgrade pip and install build tools
RUN pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ binutils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies (add official Torch index for CPU packages)
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Download only MiniLM-L6-v2 model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Aggressive cleanup: Remove extra models, HF cache, and dev tools
RUN set -e; \
    # Remove all HF models except MiniLM-L6-v2, only if folder exists
    if ls /root/.cache/huggingface/hub/models--* 2>/dev/null; then \
      find /root/.cache/huggingface/hub/models--* ! -name "models--sentence-transformers--all-MiniLM-L6-v2" -exec rm -rf {} +; \
    fi; \
    # Clean up in the MiniLM folder
    if [ -d /root/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2 ]; then \
      find /root/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2 -type f \
        ! -name 'config.json' \
        ! -name 'pytorch_model.bin' \
        ! -name 'sentence_bert_config.json' \
        ! -name 'tokenizer.json' -delete; \
    fi; \
    # Remove pip and apt caches, strip binaries
    pip cache purge; \
    apt-get purge -y --auto-remove gcc g++ binutils; \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy your application code
COPY . .

ENV INPUT_DIR=/app/input \
    OUTPUT_DIR=/app/output \
    PYTHONPATH=/app

RUN mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

CMD ["python", "main.py"]
