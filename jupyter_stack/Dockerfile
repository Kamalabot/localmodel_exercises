FROM quay.io/jupyter/pytorch-notebook:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev g++ && apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Layer 1: Core Math & Accelerated Data Processing
RUN pip install --no-cache-dir numpy scipy pandas polars dask openpyxl xlrd

# Layer 2: Vector DBs & Database Connectors
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary pymongo redis qdrant-client chromadb

# Layer 3: Heavy AI Frameworks (TensorFlow & ONNX)
RUN pip install --no-cache-dir tensorflow keras onnxruntime opencv-python-headless

# Layer 4: LLMs, Agents & NLP Ecosystem
RUN pip install --no-cache-dir transformers datasets tiktoken langchain langgraph crewai

# Layer 5: App Frontends, Visualization & Deployment
RUN pip install --no-cache-dir matplotlib seaborn plotly folium fastapi uvicorn pydantic streamlit gradio dash

# Layer 6: Lateral Analytics (Time Series, Geospatial, XAI, Graph)
RUN pip install --no-cache-dir statsmodels prophet sktime geopandas shapely rasterio optuna "ray[tune]" shap lime pymc arviz networkx pyvis librosa