#  Persona-Driven Document Intelligence

FROM python:3.9-slim

WORKDIR /app

########## 1. Install only essential build tools ##########
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ binutils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

########## 2. Python CPU-only deps (slim, no cache) ##########
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

########## 3. Download ONLY MiniLM-L6-v2 transformer ##########
RUN python - <<'PY'
from sentence_transformers import SentenceTransformer
SentenceTransformer('all-MiniLM-L6-v2')
PY

########## 4. Aggressive Cleanup: Models, torch, cache, docs, stripping ##########
RUN set -e; \
    # Delete all HF models except MiniLM-L6-v2
    find /root/.cache/huggingface/hub/models--* \
      ! -name "models--sentence-transformers--all-MiniLM-L6-v2" -exec rm -rf {} + ; \
    # In the MiniLM folder, delete tokenizers, pytorch_model.bin.index.json if present
    find /root/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2 -type f \
      ! -name 'config.json' ! -name 'pytorch_model.bin' ! -name 'sentence_bert_config.json' ! -name 'tokenizer.json' -delete || true; \
    # Remove all extra HF cache files
    find /root/.cache -type f \( -name '*.msgpack' -o -name '*.json' \) ! -name 'config.json' -delete; \
    # Remove CUDA-related/dynamic torch lib, binaries and tests/examples/docs/pycache
    find /usr/local/lib/python3.9 -type d \( -name '__pycache__' -o -name 'tests' -o -name 'test' -o -name 'examples' -o -name 'docs' -o -name 'doc' \) -exec rm -rf {} + || true; \
    find /usr/local/lib/python3.9/site-packages/torch -type f \
      \( -name '*cuda*.so' -o -name '*cublas*' -o -name '*.pdb' \) -delete || true; \
    # Strip all binaries of debug symbols
    find /usr/local/lib/python3.9/site-packages -type f \( -name '*.so' -o -name '*.pyd' \) -exec strip --strip-unneeded {} + || true; \
    # Remove all downloaded wheels, pip cache, temp, build tools
    pip cache purge && \
    apt-get purge -y --auto-remove gcc g++ binutils && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

########## 5. Project code ##########
COPY . .

ENV INPUT_DIR=/app/input \
    OUTPUT_DIR=/app/output \
    PYTHONPATH=/app

RUN mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

CMD ["python", "main.py"]
