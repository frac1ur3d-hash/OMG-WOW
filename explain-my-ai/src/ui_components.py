import streamlit as st

def inject_premium_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* Apply custom premium font */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            border: 1px solid rgba(0, 242, 254, 0.3);
            box-shadow: 0 10px 40px 0 rgba(0, 242, 254, 0.1);
            transform: translateY(-2px);
        }
        
        /* Header styles */
        .main-title {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }
        
        .sub-title {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-weight: 300;
        }
        
        /* Custom Section Titles */
        .section-header {
            font-weight: 700;
            font-size: 1.3rem;
            color: #f8fafc;
            border-bottom: 2px solid rgba(0, 242, 254, 0.15);
            padding-bottom: 8px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        
        /* Badges */
        .mode-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .mode-sim {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .mode-prod {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .score-badge {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            color: #0f172a;
            border-radius: 8px;
            padding: 5px 10px;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        /* Alert Box styles */
        .alert-container {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
            color: #fbbf24;
        }
        
        /* Source Citation Box */
        .source-box {
            font-family: monospace;
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid #4facfe;
            padding: 10px;
            border-radius: 4px;
            margin-top: 5px;
            color: #e2e8f0;
            font-size: 0.85rem;
        }
        
        /* Glowing metric */
        .glow-metric {
            text-align: center;
            padding: 15px;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .glow-metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #00f2fe;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
        }
        .glow-metric-label {
            font-size: 0.85rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
