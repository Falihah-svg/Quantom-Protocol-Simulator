# ============================================================
#  Quantum Protocol & Algorithm Simulator
#  Hackathon-level Streamlit app
#  Built on top of existing Bell/GHZ simulator
# ============================================================

import streamlit as st
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import math

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Protocol Simulator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS — Dark futuristic glassmorphism theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #020b18;
    color: #c9d6e3;
}

.stApp {
    background: radial-gradient(ellipse at 20% 20%, #0a1628 0%, #020b18 50%, #07071a 100%);
    background-attachment: fixed;
}

/* Animated grid background */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #040d1e 0%, #060818 100%) !important;
    border-right: 1px solid rgba(0, 200, 255, 0.15) !important;
}

[data-testid="stSidebar"] * {
    color: #c9d6e3 !important;
}

/* ── Title ── */
.quantum-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00e5ff, #7b2fff, #00e5ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
    letter-spacing: 2px;
    margin-bottom: 0;
}

@keyframes shimmer {
    0% { background-position: 0% }
    100% { background-position: 200% }
}

.quantum-subtitle {
    font-family: 'Share Tech Mono', monospace;
    color: #4af0ff;
    font-size: 0.85rem;
    letter-spacing: 3px;
    margin-top: 4px;
    opacity: 0.7;
}

/* ── Cards / Glass panels ── */
.glass-card {
    background: rgba(8, 20, 45, 0.7);
    border: 1px solid rgba(0, 200, 255, 0.18);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(0, 200, 255, 0.06), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 20px;
}

.glass-card-purple {
    background: rgba(15, 8, 40, 0.7);
    border: 1px solid rgba(123, 47, 255, 0.25);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(123, 47, 255, 0.08);
    margin-bottom: 20px;
}

/* ── Section headers ── */
.section-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 4px;
    color: #00e5ff;
    text-transform: uppercase;
    margin-bottom: 12px;
    opacity: 0.8;
}

/* ── Metric tiles ── */
.metric-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.metric-tile {
    flex: 1;
    min-width: 120px;
    background: rgba(0, 229, 255, 0.05);
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.metric-tile .val {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #00e5ff;
}

.metric-tile .lbl {
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: #6b8fa8;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Protocol badge ── */
.protocol-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 2px;
    border: 1px solid rgba(0,229,255,0.4);
    background: rgba(0,229,255,0.08);
    color: #00e5ff;
    margin-bottom: 8px;
}

/* ── Explain box ── */
.explain-box {
    background: linear-gradient(135deg, rgba(0,229,255,0.04), rgba(123,47,255,0.06));
    border-left: 3px solid #00e5ff;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #a8c8e0;
    margin-top: 12px;
}

/* ── Step badge ── */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(123,47,255,0.15);
    border: 1px solid rgba(123,47,255,0.4);
    border-radius: 8px;
    padding: 6px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #c084fc;
    margin: 4px 2px;
}

/* ── Noise badge ── */
.noise-active {
    background: rgba(255,80,80,0.1);
    border: 1px solid rgba(255,80,80,0.35);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #ff8080;
    font-family: 'Share Tech Mono', monospace;
    display: inline-block;
    margin-top: 6px;
}

.noise-off {
    background: rgba(0,255,160,0.08);
    border: 1px solid rgba(0,255,160,0.3);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #00ffa0;
    font-family: 'Share Tech Mono', monospace;
    display: inline-block;
    margin-top: 6px;
}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div,
.stSlider > div {
    background: transparent !important;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0a2040, #0d1a35) !important;
    border: 1px solid rgba(0,229,255,0.35) !important;
    color: #00e5ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 12px rgba(0,229,255,0.1) !important;
}

div[data-testid="stButton"] button:hover {
    border-color: #00e5ff !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.3) !important;
    transform: translateY(-1px) !important;
}

/* Code block */
.stCode, code, pre {
    background: rgba(4, 12, 28, 0.9) !important;
    border: 1px solid rgba(0,200,255,0.15) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #4af0ff !important;
}

/* Divider */
hr {
    border-color: rgba(0,229,255,0.1) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(4, 12, 28, 0.6) !important;
    border-radius: 12px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 1px !important;
    color: #6b8fa8 !important;
    border-radius: 10px !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(0,229,255,0.1) !important;
    color: #00e5ff !important;
}

/* Info/warning boxes */
.stAlert {
    background: rgba(0,229,255,0.05) !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
    border-radius: 10px !important;
    color: #a8c8e0 !important;
}

/* JSON */
.stJson {
    background: rgba(4,12,28,0.8) !important;
    border-radius: 10px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #020b18; }
::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────
if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "playing" not in st.session_state:
    st.session_state.playing = False
if "last_counts" not in st.session_state:
    st.session_state.last_counts = None
if "last_circuit" not in st.session_state:
    st.session_state.last_circuit = None
if "last_protocol" not in st.session_state:
    st.session_state.last_protocol = None


# ─────────────────────────────────────────────────────────────
# PROTOCOL DEFINITIONS — metadata & explanations
# ─────────────────────────────────────────────────────────────
PROTOCOLS = {
    "Bell State": {
        "icon": "🔔",
        "tag": "ENTANGLEMENT",
        "desc": "Creates maximally entangled 2-qubit pairs. Measuring one qubit instantly determines the other.",
        "steps": [
            ("Initialize", "All qubits start in |0⟩ ground state."),
            ("Hadamard Gate", "H on qubit 0 → creates superposition: |0⟩ + |1⟩ / √2"),
            ("CNOT Gate(s)", "Entangles qubit 0 with each target — creates |00⟩ + |11⟩ correlation."),
            ("Measure", "Collapse superposition — results are always correlated pairs."),
        ],
        "classical_note": "Classical bits: fully independent. Quantum: measuring one determines all others instantly.",
    },
    "GHZ State": {
        "icon": "🌐",
        "tag": "MULTI-QUBIT ENTANGLEMENT",
        "desc": "Greenberger–Horne–Zeilinger state — extends Bell entanglement to N qubits simultaneously.",
        "steps": [
            ("Initialize", "All N qubits in |0⟩."),
            ("Hadamard Gate", "H on qubit 0 creates superposition."),
            ("Chain CNOTs", "CNOT(0→1), CNOT(1→2)... chains entanglement like a quantum domino effect."),
            ("Measure", "All qubits collapse to same value: either all |0⟩ or all |1⟩."),
        ],
        "classical_note": "Classical: N independent coins. Quantum: N coins that always land the same face.",
    },
    "Quantum Teleportation": {
        "icon": "📡",
        "tag": "TELEPORTATION",
        "desc": "Transfers quantum state from Alice to Bob using entanglement + classical communication. No physical particle moves.",
        "steps": [
            ("Initialize", "3 qubits: q0 = message, q1/q2 = entangled Bell pair shared by Alice and Bob."),
            ("Bell Pair", "Create entanglement between Alice (q1) and Bob (q2)."),
            ("Alice's Bell Measure", "Alice applies CNOT(q0→q1) + H(q0) then measures q0 and q1."),
            ("Classical Channel", "Alice sends 2 classical bits to Bob over regular communication."),
            ("Bob's Correction", "Bob applies X and/or Z gates based on Alice's bits — recovers original state."),
        ],
        "classical_note": "Classical teleportation impossible — quantum state can't be copied (No-Cloning theorem). This protocol works despite that.",
    },
    "BB84 QKD": {
        "icon": "🔐",
        "tag": "QUANTUM CRYPTOGRAPHY",
        "desc": "First quantum key distribution protocol. Alice sends qubits in random bases; eavesdropping is physically detectable.",
        "steps": [
            ("Alice Prepares", "Alice encodes random bits in random bases: {|0⟩,|1⟩} or {|+⟩,|−⟩}."),
            ("Quantum Channel", "Alice sends qubits to Bob through quantum channel."),
            ("Bob Measures", "Bob measures in randomly chosen bases — correct base = correct bit."),
            ("Basis Sifting", "Alice & Bob compare bases over classical channel, keep only matching ones."),
            ("Key Extraction", "Matching-basis results form the shared secret key."),
        ],
        "classical_note": "Classical keys can be intercepted silently. In BB84, any eavesdropping disturbs qubits — making intrusion physically detectable.",
    },
}


# ─────────────────────────────────────────────────────────────
# CIRCUIT BUILDERS
# ─────────────────────────────────────────────────────────────

def build_bell_state(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(1, n):
        qc.cx(0, i)
    qc.measure(range(n), range(n))
    return qc


def build_ghz_state(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure(range(n), range(n))
    return qc


def build_teleportation() -> QuantumCircuit:
    # 3 qubits: q0=message, q1=Alice, q2=Bob  |  2 classical bits
    qc = QuantumCircuit(3, 3)
    # Prepare message qubit in |+⟩
    qc.h(0)
    qc.barrier(label="MSG")
    # Create Bell pair between Alice (q1) and Bob (q2)
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier(label="BELL")
    # Alice's Bell measurement
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier(label="ALICE")
    qc.measure([0, 1], [0, 1])
    # Bob's correction (classically controlled)
    with qc.if_else((qc.clbits[1], 1), QuantumCircuit(1), None, [2], []):
        pass
    qc.cx(1, 2)
    qc.cz(0, 2)
    qc.measure(2, 2)
    return qc


def build_teleportation_simple() -> QuantumCircuit:
    """Simplified teleportation without dynamic circuits for AerSimulator compatibility."""
    qc = QuantumCircuit(3, 3)
    qc.h(0)          # message in |+⟩
    qc.barrier()
    qc.h(1)          # Bell pair
    qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1)      # Alice's operations
    qc.h(0)
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    qc.cx(1, 2)      # Bob corrections (always applied for simulation)
    qc.cz(0, 2)
    qc.measure(2, 2)
    return qc


def build_bb84(n_bits: int = 4) -> QuantumCircuit:
    """Simulate BB84 key generation for n_bits."""
    # 2*n qubits: first n = Alice's, second n = Bob's (via teleportation)
    # Simplified: encode Alice's random bits in random bases
    qc = QuantumCircuit(n_bits, n_bits)
    rng = np.random.default_rng(42)
    alice_bits  = rng.integers(0, 2, n_bits)
    alice_bases = rng.integers(0, 2, n_bits)  # 0=Z-basis, 1=X-basis
    for i in range(n_bits):
        if alice_bits[i] == 1:
            qc.x(i)                 # |1⟩
        if alice_bases[i] == 1:
            qc.h(i)                 # Rotate to X-basis
    qc.barrier(label="SEND")
    bob_bases = rng.integers(0, 2, n_bits)
    for i in range(n_bits):
        if bob_bases[i] == 1:
            qc.h(i)                 # Measure in X-basis
    qc.measure(range(n_bits), range(n_bits))
    return qc, alice_bits, alice_bases, bob_bases


# ─────────────────────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────

def run_simulation(qc: QuantumCircuit, shots: int = 500, noisy: bool = False) -> dict:
    simulator = AerSimulator()
    if noisy:
        noise_model = NoiseModel()
        error = depolarizing_error(0.02, 1)
        error2 = depolarizing_error(0.04, 2)
        noise_model.add_all_qubit_quantum_error(error, ['h', 'x', 'z'])
        noise_model.add_all_qubit_quantum_error(error2, ['cx', 'cz'])
        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=shots, noise_model=noise_model)
    else:
        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=shots)
    return job.result().get_counts()


# ─────────────────────────────────────────────────────────────
# 3D VISUALIZATION — glowing qubit spheres + entanglement lines
# ─────────────────────────────────────────────────────────────

def make_3d_viz(n_qubits: int, protocol: str, counts: dict = None):
    angles = [2 * math.pi * i / n_qubits for i in range(n_qubits)]
    radius = 2.2 if n_qubits > 2 else 1.5
    xs = [radius * math.cos(a) for a in angles]
    ys = [radius * math.sin(a) for a in angles]
    zs = [0.0] * n_qubits

    # Determine qubit activation from top result
    activated = [False] * n_qubits
    if counts:
        top_state = max(counts, key=counts.get)
        for i, bit in enumerate(reversed(top_state)):
            if i < n_qubits:
                activated[i] = (bit == "1")

    fig = go.Figure()

    # ── Entanglement lines ──
    if protocol in ("Bell State", "GHZ State", "Quantum Teleportation"):
        pairs = [(0, i) for i in range(1, n_qubits)] if protocol == "Bell State" else \
                [(i, i+1) for i in range(n_qubits - 1)]
        for (a, b) in pairs:
            for t in np.linspace(0, 1, 30):
                pass  # parametric, we just draw straight lines
            fig.add_trace(go.Scatter3d(
                x=[xs[a], xs[b]], y=[ys[a], ys[b]], z=[zs[a], zs[b]],
                mode="lines",
                line=dict(color="rgba(0,229,255,0.35)", width=4),
                showlegend=False,
                hoverinfo="skip",
            ))
            # Glow line
            fig.add_trace(go.Scatter3d(
                x=[xs[a], xs[b]], y=[ys[a], ys[b]], z=[zs[a], zs[b]],
                mode="lines",
                line=dict(color="rgba(0,229,255,0.08)", width=16),
                showlegend=False,
                hoverinfo="skip",
            ))

    # ── Qubit spheres ──
    colors = ["#00e5ff" if not activated[i] else "#ff6b9d" for i in range(n_qubits)]
    sizes  = [22 if not activated[i] else 28 for i in range(n_qubits)]

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text",
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.9,
            line=dict(width=2, color="rgba(255,255,255,0.3)"),
        ),
        text=[f"q{i}" for i in range(n_qubits)],
        textposition="top center",
        textfont=dict(family="Share Tech Mono", size=13, color="#ffffff"),
        hovertext=[
            f"Qubit {i}<br>State: {'|1⟩' if activated[i] else '|0⟩'}"
            for i in range(n_qubits)
        ],
        hoverinfo="text",
        showlegend=False,
    ))

    # ── Glow halos ──
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers",
        marker=dict(
            size=[s + 14 for s in sizes],
            color=[c.replace("ff", "33") if "#" in c else c for c in colors],
            opacity=0.18,
            line=dict(width=0),
        ),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(2,11,24,0)",
        plot_bgcolor="rgba(2,11,24,0)",
        scene=dict(
            bgcolor="rgba(2,11,24,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# BAR CHART
# ─────────────────────────────────────────────────────────────

def make_bar_chart(counts: dict, protocol: str, noisy: bool):
    states = list(counts.keys())
    values = list(counts.values())
    total = sum(values)
    probs = [v / total for v in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=states, y=values,
        text=[f"{p:.1%}" for p in probs],
        textposition="outside",
        marker=dict(
            color=values,
            colorscale=[[0, "#1a0a4a"], [0.5, "#0a2a6a"], [1, "#00e5ff"]],
            line=dict(color="rgba(0,229,255,0.6)", width=1),
        ),
        hovertemplate="<b>|%{x}⟩</b><br>Counts: %{y}<br>Probability: %{text}<extra></extra>",
    ))

    noise_tag = "  ⚠ NOISY" if noisy else "  ✓ IDEAL"
    fig.update_layout(
        title=dict(
            text=f"<span style='font-family:Orbitron;font-size:13px;color:#00e5ff;letter-spacing:2px'>"
                 f"MEASUREMENT DISTRIBUTION — {protocol.upper()}{noise_tag}</span>",
            x=0.01,
        ),
        paper_bgcolor="rgba(4,12,28,0.6)",
        plot_bgcolor="rgba(4,12,28,0)",
        xaxis=dict(
            title="Basis State",
            color="#6b8fa8",
            gridcolor="rgba(0,229,255,0.06)",
            tickfont=dict(family="Share Tech Mono", color="#4af0ff"),
        ),
        yaxis=dict(
            title="Counts",
            color="#6b8fa8",
            gridcolor="rgba(0,229,255,0.06)",
        ),
        font=dict(family="Inter", color="#c9d6e3"),
        margin=dict(l=40, r=20, t=60, b=40),
        height=320,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# BB84 KEY TABLE
# ─────────────────────────────────────────────────────────────

def show_bb84_table(alice_bits, alice_bases, bob_bases, counts):
    n = len(alice_bits)
    bob_results = list(max(counts, key=counts.get))
    bob_bits = [int(b) for b in reversed(bob_results[:n])]

    rows = []
    key_bits = []
    for i in range(n):
        match = alice_bases[i] == bob_bases[i]
        ab = "Z" if alice_bases[i] == 0 else "X"
        bb = "Z" if bob_bases[i] == 0 else "X"
        keep = "✅ KEY BIT" if match else "❌ Discard"
        if match:
            key_bits.append(str(alice_bits[i]))
        rows.append({
            "Bit": i,
            "Alice Bit": alice_bits[i],
            "Alice Basis": ab,
            "Bob Basis": bb,
            "Bob Measured": bob_bits[i] if i < len(bob_bits) else "?",
            "Sifted": keep,
        })

    key = "".join(key_bits)
    return rows, key


# ─────────────────────────────────────────────────────────────
# STEP-BY-STEP CIRCUIT SLICES
# ─────────────────────────────────────────────────────────────

def get_circuit_steps(protocol: str, n_qubits: int):
    """Returns list of (label, QuantumCircuit) for step-by-step mode."""
    steps = []

    if protocol == "Bell State":
        qc0 = QuantumCircuit(n_qubits, n_qubits)
        steps.append(("Initialize |0...0⟩", qc0.copy()))
        qc0.h(0)
        steps.append(("Apply H on q0", qc0.copy()))
        for i in range(1, n_qubits):
            qc0.cx(0, i)
            steps.append((f"CNOT(0→{i})", qc0.copy()))
        qc0.measure(range(n_qubits), range(n_qubits))
        steps.append(("Measure All", qc0.copy()))

    elif protocol == "GHZ State":
        qc0 = QuantumCircuit(n_qubits, n_qubits)
        steps.append(("Initialize |0...0⟩", qc0.copy()))
        qc0.h(0)
        steps.append(("Apply H on q0", qc0.copy()))
        for i in range(n_qubits - 1):
            qc0.cx(i, i + 1)
            steps.append((f"CNOT({i}→{i+1})", qc0.copy()))
        qc0.measure(range(n_qubits), range(n_qubits))
        steps.append(("Measure All", qc0.copy()))

    elif protocol == "Quantum Teleportation":
        qc0 = QuantumCircuit(3, 3)
        steps.append(("Initialize 3 Qubits", qc0.copy()))
        qc0.h(0)
        steps.append(("H on q0 → message |+⟩", qc0.copy()))
        qc0.h(1); qc0.cx(1, 2)
        steps.append(("Bell Pair: q1–q2 Entangled", qc0.copy()))
        qc0.cx(0, 1); qc0.h(0)
        steps.append(("Alice: CNOT + H on message", qc0.copy()))
        qc0.measure([0, 1], [0, 1])
        steps.append(("Alice Measures q0, q1", qc0.copy()))
        qc0.cx(1, 2); qc0.cz(0, 2)
        steps.append(("Bob Applies Corrections", qc0.copy()))
        qc0.measure(2, 2)
        steps.append(("Bob Measures q2", qc0.copy()))

    elif protocol == "BB84 QKD":
        n = n_qubits
        qc0, ab, abas, bbas = build_bb84(n)
        qc1 = QuantumCircuit(n, n)
        steps.append(("Alice Initializes Qubits", qc1.copy()))
        rng = np.random.default_rng(42)
        ab2  = rng.integers(0, 2, n)
        abas2 = rng.integers(0, 2, n)
        for i in range(n):
            if ab2[i] == 1:
                qc1.x(i)
        steps.append(("Alice Encodes Bits (X gates)", qc1.copy()))
        for i in range(n):
            if abas2[i] == 1:
                qc1.h(i)
        steps.append(("Alice Rotates Bases (H gates)", qc1.copy()))
        bbas2 = rng.integers(0, 2, n)
        for i in range(n):
            if bbas2[i] == 1:
                qc1.h(i)
        steps.append(("Bob Measures in Random Bases", qc1.copy()))
        qc1.measure(range(n), range(n))
        steps.append(("Measure & Sift Key", qc1.copy()))

    return steps


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px'>
        <div style='font-family:Orbitron;font-size:1.1rem;font-weight:800;
                    background:linear-gradient(90deg,#00e5ff,#7b2fff);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    letter-spacing:2px'>QUANTUM</div>
        <div style='font-family:Share Tech Mono;font-size:0.6rem;letter-spacing:4px;
                    color:#4af0ff;opacity:0.6;margin-top:2px'>PROTOCOL SIMULATOR</div>
    </div>
    <hr style='border-color:rgba(0,229,255,0.1);margin:8px 0 20px'>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">▸ Protocol</div>', unsafe_allow_html=True)
    protocol = st.selectbox(
        "Protocol",
        options=list(PROTOCOLS.keys()),
        format_func=lambda x: f"{PROTOCOLS[x]['icon']}  {x}",
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label" style="margin-top:20px">▸ Qubits</div>', unsafe_allow_html=True)

    if protocol == "Quantum Teleportation":
        st.markdown(
            '<div style="font-family:Share Tech Mono;font-size:0.72rem;color:#c084fc;'
            'background:rgba(123,47,255,0.1);border:1px solid rgba(123,47,255,0.3);'
            'border-radius:8px;padding:8px 12px;margin-bottom:10px">'
            '⚠ Teleportation uses fixed 3 qubits</div>',
            unsafe_allow_html=True
        )
        num_qubits = 3
    elif protocol == "BB84 QKD":
        num_qubits = st.slider("Key Bits", 2, 5, 4, label_visibility="collapsed")
    else:
        num_qubits = st.slider("Qubits", 2, 5, 2, label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top:20px">▸ Options</div>', unsafe_allow_html=True)
    noisy = st.toggle("⚠ Noise Simulation", value=False)
    explain_mode = st.toggle("💡 Explain Mode", value=True)

    st.markdown('<div class="section-label" style="margin-top:20px">▸ Controls</div>', unsafe_allow_html=True)
    col_run, col_rst = st.columns(2)
    with col_run:
        run_btn = st.button("▶ RUN", use_container_width=True)
    with col_rst:
        reset_btn = st.button("↺ RESET", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-label">▸ Step Mode</div>', unsafe_allow_html=True)
    steps_list = get_circuit_steps(protocol, num_qubits)
    step_prev, step_next = st.columns(2)
    with step_prev:
        if st.button("◀ PREV", use_container_width=True):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
    with step_next:
        if st.button("NEXT ▶", use_container_width=True):
            st.session_state.step_index = min(len(steps_list) - 1, st.session_state.step_index + 1)

    step_idx = st.slider(
        "Step",
        0, len(steps_list) - 1,
        st.session_state.step_index,
        label_visibility="collapsed"
    )
    st.session_state.step_index = step_idx

    if reset_btn:
        st.session_state.last_counts = None
        st.session_state.last_circuit = None
        st.session_state.step_index = 0
        st.rerun()


# ─────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────

st.markdown(f"""
<div style='padding: 8px 0 24px'>
    <div class='quantum-title'>QUANTUM PROTOCOL SIMULATOR</div>
    <div class='quantum-subtitle'>⚛ INTERACTIVE QUANTUM ALGORITHM RESEARCH PLATFORM &nbsp;·&nbsp; QISKIT + AERSIMULATOR</div>
</div>
""", unsafe_allow_html=True)

# Protocol info banner
meta = PROTOCOLS[protocol]
st.markdown(f"""
<div class='glass-card' style='padding:16px 24px;margin-bottom:24px'>
    <span class='protocol-badge'>{meta['tag']}</span>
    <span style='margin-left:12px;font-size:1.1rem'>{meta['icon']} <strong style="color:#e8f0f8">{protocol}</strong></span>
    <div style='color:#8aacbf;font-size:0.88rem;margin-top:8px;line-height:1.6'>{meta['desc']}</div>
    {'<div class="noise-active">⚠ NOISE MODEL ACTIVE — Depolarizing errors enabled</div>' if noisy else '<div class="noise-off">✓ IDEAL SIMULATION — No decoherence</div>'}
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────

tab_sim, tab_step, tab_3d, tab_compare, tab_about = st.tabs([
    "⚡ SIMULATION", "🔬 STEP MODE", "🌐 3D VIEW", "⚖ COMPARE", "📖 ABOUT"
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — SIMULATION
# ══════════════════════════════════════════════════════════════
with tab_sim:

    # Run simulation
    if run_btn:
        with st.spinner(""):
            if protocol == "Bell State":
                qc = build_bell_state(num_qubits)
                counts = run_simulation(qc, noisy=noisy)
            elif protocol == "GHZ State":
                qc = build_ghz_state(num_qubits)
                counts = run_simulation(qc, noisy=noisy)
            elif protocol == "Quantum Teleportation":
                qc = build_teleportation_simple()
                counts = run_simulation(qc, noisy=noisy)
                num_qubits = 3
            elif protocol == "BB84 QKD":
                qc, alice_bits, alice_bases, bob_bases = build_bb84(num_qubits)
                counts = run_simulation(qc, noisy=noisy)
                st.session_state.bb84_data = (alice_bits, alice_bases, bob_bases)

            st.session_state.last_counts = counts
            st.session_state.last_circuit = qc
            st.session_state.last_protocol = protocol

    counts = st.session_state.last_counts
    qc     = st.session_state.last_circuit

    if counts is None:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;opacity:0.4'>
            <div style='font-family:Orbitron;font-size:3rem;margin-bottom:16px'>⚛</div>
            <div style='font-family:Share Tech Mono;letter-spacing:4px;font-size:0.8rem;color:#4af0ff'>
                SELECT PROTOCOL → CLICK RUN
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total = sum(counts.values())
        top_state = max(counts, key=counts.get)
        n_states = len(counts)

        # Metric tiles
        st.markdown(f"""
        <div class='metric-row'>
            <div class='metric-tile'>
                <div class='val'>{total}</div>
                <div class='lbl'>Shots</div>
            </div>
            <div class='metric-tile'>
                <div class='val'>{n_states}</div>
                <div class='lbl'>Unique States</div>
            </div>
            <div class='metric-tile'>
                <div class='val'>|{top_state}⟩</div>
                <div class='lbl'>Top State</div>
            </div>
            <div class='metric-tile'>
                <div class='val'>{counts[top_state]/total:.0%}</div>
                <div class='lbl'>Top Prob</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chart + counts
        col_chart, col_counts = st.columns([3, 1])
        with col_chart:
            st.plotly_chart(make_bar_chart(counts, protocol, noisy), use_container_width=True)
        with col_counts:
            st.markdown('<div class="section-label" style="margin-top:12px">Raw Counts</div>', unsafe_allow_html=True)
            st.json(counts)

        # Circuit diagram
        st.markdown('<div class="section-label" style="margin-top:8px">▸ Circuit Diagram</div>', unsafe_allow_html=True)
        st.code(str(qc.draw(output="text")), language="text")

        # BB84 Key Table
        if protocol == "BB84 QKD" and hasattr(st.session_state, "bb84_data"):
            ab, abas, bbas = st.session_state.bb84_data
            rows, key = show_bb84_table(ab, abas, bbas, counts)
            st.markdown('<div class="section-label" style="margin-top:16px">▸ BB84 Key Sifting</div>', unsafe_allow_html=True)
            st.dataframe(rows, use_container_width=True)
            st.markdown(f"""
            <div class='glass-card-purple' style='padding:14px 20px'>
                <div class='section-label'>Sifted Key</div>
                <div style='font-family:Share Tech Mono;font-size:1.4rem;color:#c084fc;letter-spacing:6px'>{key if key else "No matching bases"}</div>
                <div style='font-size:0.78rem;color:#6b8fa8;margin-top:6px'>{len(key)} bits retained from {len(ab)} transmitted</div>
            </div>
            """, unsafe_allow_html=True)

        # Explain Mode
        if explain_mode:
            st.markdown('<div class="section-label" style="margin-top:16px">▸ Explain Mode</div>', unsafe_allow_html=True)
            step_explains = meta["steps"]
            for i, (title, desc) in enumerate(step_explains):
                st.markdown(f"""
                <div class='explain-box' style='margin-bottom:8px'>
                    <span style='font-family:Orbitron;font-size:0.7rem;color:#00e5ff;letter-spacing:2px'>STEP {i+1} — {title.upper()}</span><br>
                    <span>{desc}</span>
                </div>
                """, unsafe_allow_html=True)

            # Classical comparison
            st.markdown(f"""
            <div class='glass-card-purple' style='padding:14px 20px;margin-top:8px'>
                <div class='section-label'>⚖ Quantum vs Classical</div>
                <div style='font-size:0.86rem;color:#c9d6e3;line-height:1.7'>{meta["classical_note"]}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — STEP MODE
# ══════════════════════════════════════════════════════════════
with tab_step:
    idx = st.session_state.step_index
    step_label, step_qc = steps_list[idx]

    st.markdown(f"""
    <div class='glass-card' style='padding:16px 24px;margin-bottom:20px'>
        <div class='section-label'>Step {idx + 1} of {len(steps_list)}</div>
        <div style='font-family:Orbitron;font-size:1rem;color:#00e5ff;letter-spacing:2px'>{step_label.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar via markdown
    progress = (idx + 1) / len(steps_list)
    bar_filled = int(progress * 30)
    bar_str = "█" * bar_filled + "░" * (30 - bar_filled)
    st.markdown(f"""
    <div style='font-family:Share Tech Mono;font-size:0.75rem;color:#4af0ff;margin-bottom:16px'>
        [{bar_str}] {progress:.0%}
    </div>
    """, unsafe_allow_html=True)

    # Step badges
    badges = ""
    for i, (lbl, _) in enumerate(steps_list):
        active = "background:rgba(0,229,255,0.15);border-color:rgba(0,229,255,0.6);color:#00e5ff;" if i == idx else ""
        badges += f"<span class='step-badge' style='{active}'>{i+1}. {lbl}</span>"
    st.markdown(f"<div style='margin-bottom:20px'>{badges}</div>", unsafe_allow_html=True)

    # Circuit at this step
    st.markdown('<div class="section-label">▸ Circuit State</div>', unsafe_allow_html=True)
    st.code(str(step_qc.draw(output="text")), language="text")

    # Step explanation
    if explain_mode and idx < len(meta["steps"]):
        title, desc = meta["steps"][min(idx, len(meta["steps"]) - 1)]
        st.markdown(f"""
        <div class='explain-box'>
            <strong style='color:#00e5ff;font-family:Orbitron;font-size:0.7rem;letter-spacing:2px'>{title.upper()}</strong><br>
            {desc}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — 3D VIEW
# ══════════════════════════════════════════════════════════════
with tab_3d:
    st.markdown('<div class="section-label">▸ Qubit Entanglement Map</div>', unsafe_allow_html=True)
    counts_for_3d = st.session_state.last_counts
    fig3d = make_3d_viz(num_qubits, protocol, counts_for_3d)
    st.plotly_chart(fig3d, use_container_width=True)

    legend_html = """
    <div class='glass-card' style='padding:14px 20px'>
        <div class='section-label'>Legend</div>
        <div style='display:flex;gap:24px;flex-wrap:wrap;font-size:0.82rem'>
            <span>🔵 <span style='color:#00e5ff'>Qubit in |0⟩</span></span>
            <span>🔴 <span style='color:#ff6b9d'>Qubit in |1⟩ (top result)</span></span>
            <span>〰 <span style='color:#4af0ff'>Entanglement Line</span></span>
        </div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    if counts_for_3d is None:
        st.info("Run a simulation first to see qubit state coloring.")


# ══════════════════════════════════════════════════════════════
# TAB 4 — COMPARE MODE
# ══════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("""
    <div class='glass-card' style='padding:16px 24px;margin-bottom:16px'>
        <div class='section-label'>⚖ Ideal vs Noisy Comparison</div>
        <div style='color:#8aacbf;font-size:0.86rem'>
            Runs the same protocol twice — once with an ideal simulator and once with
            a depolarizing noise model (2% per gate) — so you can see decoherence effects.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ RUN COMPARISON", use_container_width=False):
        with st.spinner("Running ideal + noisy simulations..."):
            if protocol == "Bell State":
                qc_c = build_bell_state(num_qubits)
            elif protocol == "GHZ State":
                qc_c = build_ghz_state(num_qubits)
            elif protocol == "Quantum Teleportation":
                qc_c = build_teleportation_simple()
            else:
                qc_c, _, _, _ = build_bb84(num_qubits)

            counts_ideal = run_simulation(qc_c, shots=500, noisy=False)
            counts_noisy = run_simulation(qc_c, shots=500, noisy=True)

        col_i, col_n = st.columns(2)
        with col_i:
            st.markdown('<div class="noise-off" style="margin-bottom:10px">✓ IDEAL</div>', unsafe_allow_html=True)
            st.plotly_chart(make_bar_chart(counts_ideal, protocol, False), use_container_width=True)
        with col_n:
            st.markdown('<div class="noise-active" style="margin-bottom:10px">⚠ NOISY</div>', unsafe_allow_html=True)
            st.plotly_chart(make_bar_chart(counts_noisy, protocol, True), use_container_width=True)

        # Fidelity estimate
        all_states = set(counts_ideal) | set(counts_noisy)
        total = 500
        fidelity = sum(
            math.sqrt((counts_ideal.get(s, 0) / total) * (counts_noisy.get(s, 0) / total))
            for s in all_states
        )
        st.markdown(f"""
        <div class='glass-card-purple' style='padding:14px 24px;text-align:center'>
            <div class='section-label'>Estimated Fidelity</div>
            <div style='font-family:Orbitron;font-size:2rem;color:#c084fc'>{fidelity:.3f}</div>
            <div style='font-size:0.78rem;color:#6b8fa8;margin-top:4px'>
                1.000 = perfect · closer to 0 = high noise degradation
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Click 'RUN COMPARISON' to compare ideal vs noisy outcomes.")


# ══════════════════════════════════════════════════════════════
# TAB 5 — ABOUT
# ══════════════════════════════════════════════════════════════
with tab_about:
    st.markdown("""
    <div class='glass-card'>
        <div style='font-family:Orbitron;font-size:0.9rem;color:#00e5ff;letter-spacing:3px;margin-bottom:16px'>
            ABOUT THIS PLATFORM
        </div>
        <div style='font-size:0.9rem;line-height:1.9;color:#a8c8e0'>
            <strong style='color:#e8f0f8'>Quantum Protocol & Algorithm Simulator</strong> is an interactive
            research and education platform for exploring quantum computing protocols without physical quantum hardware.<br><br>
            Built with <strong style='color:#00e5ff'>Qiskit</strong> (IBM's open-source quantum SDK) and
            <strong style='color:#00e5ff'>AerSimulator</strong> for high-fidelity statevector simulation.
        </div>
    </div>

    <div class='glass-card-purple'>
        <div style='font-family:Orbitron;font-size:0.8rem;color:#c084fc;letter-spacing:3px;margin-bottom:16px'>
            PROTOCOLS
        </div>
    """, unsafe_allow_html=True)

    for name, m in PROTOCOLS.items():
        st.markdown(f"""
        <div style='margin-bottom:14px;padding:12px 16px;background:rgba(255,255,255,0.03);border-radius:10px'>
            <strong style='color:#e8f0f8'>{m['icon']} {name}</strong>
            <span style='margin-left:8px;font-family:Share Tech Mono;font-size:0.68rem;
                         color:#6b8fa8;letter-spacing:2px'>{m['tag']}</span>
            <div style='font-size:0.83rem;color:#8aacbf;margin-top:6px'>{m['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    </div>
    <div class='glass-card' style='margin-top:0'>
        <div style='font-family:Orbitron;font-size:0.8rem;color:#00e5ff;letter-spacing:3px;margin-bottom:12px'>TECH STACK</div>
        <div style='display:flex;gap:12px;flex-wrap:wrap'>
            <span class='protocol-badge'>Streamlit</span>
            <span class='protocol-badge'>Qiskit ≥ 1.0</span>
            <span class='protocol-badge'>qiskit-aer ≥ 0.14</span>
            <span class='protocol-badge'>Plotly</span>
            <span class='protocol-badge'>NumPy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

