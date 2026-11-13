# AGENTS.md — AI Agent Onboarding & Project Guide

> **Purpose:** This file provides immediate technical context, invariants, and exact commands so any AI coding agent can understand, spin up, verify, and extend this repository without trial and error.

---

## 1. Project Overview
- **Domain:** Academic Final Integrative Project (*Trabajo Integrador Final — AE 4*) for **Sistemas Operativos Distribuidos (2026)**.
- **System:** Distributed simulation and closed-loop control of an automated NFT hydroponic system integrating:
  1. **IoT & Pub/Sub:** Multivariable Python sensor simulators (`src/sensors/`) → **Eclipse Mosquitto** MQTT broker (`config/mosquitto/mosquitto.conf`, TCP `1883`) → **Closed-loop Controller** (`src/controller/`) + **JSON Batch Collector** (`src/collector/`).
  2. **Containerization & Orchestration:** `docker-compose.yml` for local stack & Spark Standalone; **k3s** via **k3d** (`k8s/k3d-cluster-config.yaml`, `k8s/sensor-deployment.yaml`) for 3-node Kubernetes orchestration (`1 server + 2 agents`), horizontal scaling, and pod self-healing.
  3. **Distributed Data Processing:** Identical zone-aggregation & alert-counting workload implemented across 3 engines for benchmarking:
     - Sequential Python (`src/processing/baseline_python/process_baseline.py`)
     - Hadoop Streaming MapReduce (`src/processing/hadoop/mapper.py`, `reducer.py`, `run_hadoop_job.py`)
     - Apache Spark DataFrames & Structured Streaming (`src/processing/spark/batch_analysis.py`, `streaming_processor.py`)
  4. **Infrastructure as Code (IaC):** Idempotent Ansible playbook (`ansible/playbook.yml`, `ansible/inventory.ini`).
  5. **Experiments, Visualization & Deliverables:** Automated isolated benchmark suite (`benchmarks/run_experiments.py`), plotting (`analysis/generate_plots.py`), Jupyter analysis (`analysis/exploratory_analysis.ipynb`), APA 7 report (`docs/Informe_Final_APA7_SOD_2026.pdf`), presentation (`docs/Presentacion_TIF_SOD_2026.pdf` / `.pptx`), speaker scripts (`docs/SPEECH_PERSONA_1.md`, `SPEECH_PERSONA_2.md`), live demo script (`scripts/demo_en_vivo.sh`), and MP4 backups (`docs/videos/*.mp4`).

---

## 2. Environment & Invariants (READ BEFORE RUNNING COMMANDS)
- **Host OS:** Linux (tested on CachyOS / Arch Linux with Docker Compose v5.5.1, `k3d` v5.8.3, `kubectl` v1.37.2, `ansible` core 2.22.0, `libreoffice`, `ffmpeg`).
- **Python Virtual Environment:**
  - Always create/use `.venv` at project root:
    ```bash
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    ```
  - **NEVER** install packages globally (`pip install` outside `.venv`). Always invoke `.venv/bin/python` or `.venv/bin/pip`.
- **Large Datasets Excluded from Git:**
  - `data/datasets/*.csv` (`synthetic_1M.csv` ~61 MB, `synthetic_10M.csv` ~615 MB) and `data/raw/*.json` are gitignored.
  - Regenerate deterministic datasets (`seed=42`) anytime via `make generate-data`.
- **Agronomic Rules (`src/common/config.py`):**
  - `ph > 6.5` → `DOSIFICAR_ACIDO` (`dosificador_acido`)
  - `ph < 5.5` → `DOSIFICAR_BASE` (`dosificador_base`)
  - `water_level < 30.0` → `REPONER_AGUA` (`bomba_agua`)
  - `temperature > 24.0` / `< 18.0` → `ACTIVAR_ENFRIADOR` / `ACTIVAR_CALEFACTOR`
- **k3s / Mosquitto Networking:**
  - Inside k3d pods, `ConfigMap sensor-config` points `MQTT_BROKER_HOST` to `host.k3d.internal:1883` so k3s pods reach the Docker Compose Mosquitto broker exposed on host port `1883`.

---

## 3. Repository Map
| Path | Responsibility |
| :--- | :--- |
| `Makefile` | Single entry point for setup, build, k3s, data gen, benchmarks, plots, and tests |
| `docker-compose.yml` | Mosquitto, collector, controller, sensor-simulator, Spark master & workers |
| `src/common/config.py` | Shared MQTT topics, paths, thresholds, and actuator actions |
| `src/sensors/` | Sensor node simulator (Gaussian noise, temporal drift, anomaly injection) + Dockerfile |
| `src/collector/` | MQTT subscriber writing atomic JSON batches to `data/raw/` + Dockerfile |
| `src/controller/` | Closed-loop controller emitting actuator commands & logging latencies to `data/metrics/` |
| `src/processing/` | `baseline_python/`, `hadoop/`, and `spark/` analytics implementations |
| `src/benchmarks/generate_synthetic_data.py` | Chunked NumPy dataset generator (`seed=42`) |
| `benchmarks/run_experiments.py` | Isolated subprocess benchmark runner for E1, E2, and real MQTT E5 |
| `ansible/` | Local inventory and idempotent verification playbook (`changed=0` on 2nd run) |
| `k8s/` | k3d cluster definition (`1 server + 2 agents`) and Deployment/Service/HPA manifests |
| `analysis/` | `generate_plots.py`, `exploratory_analysis.ipynb`, and 300 DPI PNG figures |
| `scripts/` | `demo_en_vivo.sh`, `record_demo_videos.py`, `build_presentation.py`, `build_apa_report.py` |
| `docs/` | APA 7 report (`.md`, `.docx`, `.pdf`), slides (`.pptx`, `.pdf`), speeches, and MP4 backups |

---

## 4. Quick Boot & Verification Commands
Run these in sequence from the repository root to bring up, verify, and tear down the full system:

```bash
# 1. Verify environment & Ansible idempotency (expect changed=0 on repeat)
make setup

# 2. Generate deterministic 1M and 10M datasets (if data/datasets/ is empty)
make generate-data

# 3. Build local Docker images & run full validation suite (Python, Hadoop, Spark 1M)
make build
make test-all

# 4. Run IoT stack locally & verify closed-loop controller reactions
docker compose up -d mosquitto collector controller sensor-simulator
docker compose logs --tail=20 controller
docker compose down

# 5. Spin up 3-node k3s cluster, deploy, scale, and test pod self-healing
make k3s-up
make k3s-deploy
kubectl scale deployment sensor-simulator --replicas=5
kubectl delete pod $(kubectl get pods -l app=sensor-simulator -o jsonpath='{.items[0].metadata.name}') --now
kubectl get pods -l app=sensor-simulator
make k3s-down

# 6. Re-run 3-repetition benchmarks (E1, E2, E5) and regenerate figures + PDFs
make benchmark
make analyze
.venv/bin/python scripts/build_presentation.py
.venv/bin/python scripts/build_apa_report.py
```

---

## 5. Observed Reference Baselines (Do Not Fabricate Metrics)
All reports and slides reflect real measurements stored in `data/metrics/*.csv`:
- **E1 (1M rows, 3 runs):** Python `3.28 ± 0.04 s` | Hadoop Streaming `4.21 ± 0.08 s` | Spark compute `5.37 ± 0.12 s`.
- **E1 (10M rows, 3 runs):** Python `34.20 ± 0.39 s` | Hadoop Streaming `38.09 ± 3.18 s` | Spark compute `8.86 ± 0.67 s` (`3.86x` faster than Python, `4.30x` faster than Hadoop).
- **E2 (Spark on 10M, 3 runs):** 1 worker `14.78 s` (`1.00x`) → 2 workers `11.09 s` (`1.33x`, `66.6%` eff.) → 3 workers `9.18 s` (`1.61x`, `53.6%` eff.).
- **E5 (Real Mosquitto + Controller):** 1 sensor `0.11 ± 0.22 ms` (P95 `0.49 ms`) | 10 sensors `2.22 ± 1.46 ms` (P95 `4.56 ms`) | 50 sensors `7.56 ± 7.03 ms` (P95 `19.56 ms`).
