# AutoPerf++

AutoPerf++ is a tool for automated performance, scalability analysis and bottleneck identification of network server applications. It consists of two main components:

- **Load Generator Machine**
- **Server-Side Agent**

Follow the steps below to set up and run AutoPerf++.

---

## 🔧 Prerequisites

- Python 3.6+
- pip3
- git
- Ubuntu-based Linux environment

---

## 🚀 Setup Instructions

### ✅ 1. Load Generator Machine

#### Step 1: Install Taurus

```bash
sudo apt update
pip3 install bzt
bzt --version  # Verify installation
```

#### Step 2: Install an Off-the-Shelf Load Generator Supported by Taurus

Taurus supports tools like JMeter, Locust, Gatling, etc. To trigger auto-download, run a sample Taurus test (you can use a simple YAML file):

```bash
bzt example_test.yml
```

#### Step 3: Clone the AutoPerf++ Repository

```bash
git clone https://github.com/HelenSathvika/MS-Project.git
```

Extract only the `AutoPerf++-load-generator-machine` folder to your working directory.

#### Step 4: Navigate to the Load Generator Directory

```bash
cd autoPerf++-load-generator-machine
```

#### Step 5: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

#### Step 6: Configure Inputs

Modify the input configuration file in the `input-configurations/` folder according to the mode you want to run.

#### Step 7: Run AutoPerf++

```bash
python3 main.py <mode_number>
```

Replace `<mode_number>` with one of the following:
- `1` — Scalability Profiling
- `2` — LLC Bottleneck Detection
- `3` — Misconfigured Soft Resource Identification
- `4` — Thread Pool Classification

---

### ✅ 2. Server-Side Agent Machine

#### Step 1: Clone the AutoPerf++ Repository

```bash
git clone https://github.com/HelenSathvika/MS-Project.git
```

Extract only the `autoPerf++-server-side-agent` folder to your desired directory.

#### Step 2: Navigate to the Agent Directory

```bash
cd autoPerf++-server-side-agent
```

#### Step 3: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

---

## 📁 Folder Structure

```
MS-Project/
├── autoPerf++-load-generator-machine/
│   ├── main.py
│   ├── requirements.txt
│   ├── input-configurations/
│   └── ...
└── autoPerf++-server-side-agent/
    ├── Run.py
    ├── requirements.txt
    └── ...
```

---


## 📞 Contact

For any questions or issues, please open an issue or pull request on the [GitHub repository](https://github.com/HelenSathvika/MS-Project).
