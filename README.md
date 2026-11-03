# Log-Based Anomaly Detection for Distributed Systems

Detects abnormal behaviour in system logs using NLP-style preprocessing and a
neural-network autoencoder.

## How it works
1. **Generate logs** (`src/generate_logs.py`): creates 20,000 synthetic log lines
   from 5 nodes, with about 1% anomalies injected in bursts (errors, timeouts, disk alerts).
2. **Preprocess** (`src/preprocess.py`): parses each line with regex, then masks
   variable parts (block IDs, IPs, numbers) so lines become reusable templates.
3. **Detect** (`src/detect.py`):
   - groups logs into windows of 10 lines
   - converts each window to a TF-IDF vector (text to numbers)
   - trains an autoencoder (neural network) on **normal windows only**
   - windows it reconstructs badly (high error) are flagged as anomalies

## Run
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/generate_logs.py
python src/preprocess.py
python src/detect.py
```

## Results
On the synthetic data: precision and recall about 0.95 for the anomaly class.

## Limitations
- The data is synthetic and easy; real logs (e.g. HDFS, BGL) are messier.
- Threshold is set at the 99th percentile of normal error, so it needs tuning.
- Next steps: test on the public HDFS log dataset, try an LSTM, add a dashboard.
