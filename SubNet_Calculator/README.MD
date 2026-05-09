# 🌐 IP Subnet Calculator

> A web-based IPv4 subnet calculator supporting Class A / B / C addressing, CIDR notation, Fixed-Length Subnet Masking (FLSM), and Variable-Length Subnet Masking (VLSM).

**Computer Networking Project — FAST NUCES Karachi**
Areeba Hasnain `23K-00059` · Emman Abrar `23K-0051`

---

## 📸 Features

- **Basic Subnet Calculator** — network address, broadcast, first/last host, binary breakdown
- **Class Detection** — automatically identifies Class A, B, C, D, E and Private/Public status
- **FLSM** — divide any network into equal-sized subnets with full allocation table
- **VLSM** — allocate variable-size subnets by host requirement with utilization stats
- **Binary Representation** — colour-coded network vs host bits for every calculation
- **CIDR Flexible Input** — accepts `/24`, `24`, or `255.255.255.0` formats
- Fully responsive dark-themed UI

---

## 🗂️ Project Structure

```
ip_calculator/
├── app.py               # Flask backend — all subnetting logic + API routes
├── requirements.txt     # Python dependencies
├── static/
│   └── style.css        # Dark theme stylesheet
└── templates/
    └── index.html       # Frontend — tabs, forms, results rendering
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ip-subnet-calculator.git
cd ip-subnet-calculator

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open your browser at **http://127.0.0.1:5000**

---

## 🚀 Usage

### Tab 1 — Basic Subnet

Enter an IPv4 address and network prefix to get full subnet details.

| Field | Example Input |
|---|---|
| IP Address | `192.168.1.0` |
| Network Prefix / CIDR | `/24` or `24` or `255.255.255.0` |

**Output includes:** Network address · Broadcast · First/Last usable host · Subnet mask · CIDR · Usable hosts · IP Class · Private/Public · Binary breakdown

---

### Tab 2 — FLSM (Fixed-Length Subnet Masking)

Split a network into equal-sized subnets. Best for uniform network segments.

| Field | Example |
|---|---|
| Network Address | `192.168.1.0` |
| Network Prefix | `/24` |
| Number of Subnets | `4` |

The calculator automatically determines bits borrowed, new prefix, block size, and generates a full allocation table for all subnets.

---

### Tab 3 — VLSM (Variable-Length Subnet Masking)

Allocate subnets of different sizes from one parent network. Most efficient use of IP address space.

**Example configuration:**

| Subnet Name | Hosts Required |
|---|---|
| Data-Center | 100 |
| Office-LAN | 50 |
| Guest-WiFi | 25 |
| Management | 10 |
| Point-to-Point | 2 |

Subnets are automatically sorted largest-first and assigned the smallest fitting prefix. Address utilization percentage is shown in the summary.

---

## 🔌 API Endpoints

The Flask backend exposes three JSON endpoints used by the frontend.

### `POST /api/basic`
```json
{ "ip": "192.168.1.0", "cidr": "/24" }
```

### `POST /api/flsm`
```json
{ "ip": "192.168.1.0", "cidr": "/24", "num_subnets": 4 }
```

### `POST /api/vlsm`
```json
{
  "ip": "192.168.1.0",
  "cidr": "/24",
  "subnets": [
    { "name": "LAN-A", "hosts": 50 },
    { "name": "LAN-B", "hosts": 10 }
  ]
}
```

All endpoints return JSON. Errors return `{ "error": "message" }` with HTTP 400.

---

## 🧮 IP Class Reference

| Class | First Octet Range | Default Prefix | Usage |
|---|---|---|---|
| A | 1 – 126 | /8 | Large networks |
| B | 128 – 191 | /16 | Medium networks |
| C | 192 – 223 | /24 | Small networks |
| D | 224 – 239 | — | Multicast |
| E | 240 – 255 | — | Experimental |

**Private ranges (RFC 1918):**
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Templating | Jinja2 |
| Fonts | Inter, JetBrains Mono (Google Fonts) |

---

## 📚 References

- Kurose, J. F., & Ross, K. W. (2021). *Computer Networking: A Top-Down Approach* (8th ed.). Pearson.
- Tanenbaum, A. S., & Wetherall, D. J. (2011). *Computer Networks* (5th ed.). Pearson.
- Postel, J. (1981). [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791). IETF.
- Mogul, J., & Postel, J. (1985). [RFC 950 — Internet Standard Subnetting Procedure](https://www.rfc-editor.org/rfc/rfc950). IETF.
- Fuller, V. et al. (1993). [RFC 1519 — CIDR: An Address Assignment and Aggregation Strategy](https://www.rfc-editor.org/rfc/rfc1519). IETF.
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

## 👥 Contributors

| Name | Student ID | Responsibilities |
|---|---|---|
| Emman Abrar | 23K-0051 | IP Input Module · Network Address Calculation · Broadcast Address Calculation · Module Integration |
| Areeba Hasnain | 23K-00059 | Subnet Calculation Engine · Host Range Calculation · Subnet Allocation · Result Display Module |

---

## 📄 License

This project was developed for academic purposes as part of the Computer Networking course at FAST NUCES Karachi.
