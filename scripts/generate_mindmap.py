#!/usr/bin/env python3
"""Generate Mermaid mind maps for each chapter's key concepts."""
import os
import sys

CHAPTER_MAPS = {
    "ch1_bop": """mindmap
  root((Ch1 BOP 国际收支))
    Concept
      Flow concept
      Residents vs Non-Residents
        Economic center of interest
        > 1 year = resident
        International orgs always non-resident
      Economic transactions
        Exchange (bilateral transfer)
        Transfer (unilateral)
    BOP Statement (BPM6)
      Current Account
        Goods and Services
        Primary Income
          Compensation of employees
          Investment income
        Secondary Income
          Current transfers
      Capital Account
        Non-produced non-financial assets
        Capital transfers
      Financial Account
        Direct Investment (FDI/ODI)
        Portfolio Investment
        Financial Derivatives
        Other Investments
        Reserve Assets
      Net Errors and Omissions
    Double-Entry Bookkeeping
      Credit: Income↑ Expenditure↓ Asset↓ Liability↑
      Debit: Income↓ Expenditure↑ Asset↑ Liability↓
      Accrual basis (NOT cash basis)
    Analysis
      Trade Balance (TB)
      Current Account Balance (CB)
      Financial Account Balance (FB)
      Overall Balance (OB)
        OB = CA + KA + FA + Errors
        OB = -Reserve Assets
    Adjustment
      Automatic
        Gold Standard: Price-Specie-Flow
        Fixed Rate: Interest + Income + Price effects
        Floating Rate: Exchange rate auto-adjust
      Policy
        FX Buffering
        Expenditure Shifting (fiscal + monetary)
        Expenditure Switching (exchange rate + direct control)
        Supply Management
    Key Theories
      Meade Conflict
        Fixed rate + single tool = dilemma
        Regions I and IV
      Tinbergen's Rule
        N targets need N tools
      Mundell's Policy Assignment
        Fiscal → Internal equilibrium
        Monetary → External equilibrium""",

    "ch2_exchange_rate": """mindmap
  root((Ch2 Exchange Rate 外汇与汇率))
    Foreign Exchange
      Dynamic: International remittance
      Static broad: FX assets and claims
      Static narrow: Payment instruments for settlement
      Three features
        Denomination in foreign currency
        Convertibility
        Payability/Universal acceptability
    Quotation Methods
      Direct Quotation
        1 foreign = XXX domestic
        China uses this
        Front buy, back sell
      Indirect Quotation
        1 domestic = XXX foreign
        UK, US, Eurozone use this
        Front sell, back buy
      USD Quotation
        1 USD = XXX other
        Interbank market
    Exchange Rate Types
      By bank: Bid, Offer, Middle, Cash rate
      By settlement: Spot (T+2), Forward (T+3+)
      By determination: Basic rate, Cross rate
      By value: Nominal, Real, Effective, Real Effective
      By speed: T/T > M/T > D/D
    Forward Rate Calculation
      Premium: Forward > Spot
      Discount: Forward < Spot
      Small-big numbers: ADD
      Big-small numbers: SUBTRACT
      Interest Rate Parity
        High rate currency → forward discount
        Low rate currency → forward premium
    Cross Rate
      USD same side: Cross divide
      USD different sides: Same side multiply
    Influencing Factors
      Long-term
        BOP situation
        Inflation rate differences
        Economic growth differences
        Macroeconomic policy
      Short-term
        Market expectations (most significant)
        Relative interest rates
        Government intervention
        Political factors
    Effects of Exchange Rate Changes
      Trade balance
        Marshall-Lerner: ηx+ηm > 1
        J-Curve Effect: 9-12 month lag
      Capital flows
      Price levels
      Employment and national income
      Foreign exchange reserves""",
}

def generate_mermaid_file(chapter_name, output_path=None):
    """Generate a .mmd file for the given chapter."""
    key = chapter_name.lower().replace(" ", "_").replace("-", "_")
    mindmap = CHAPTER_MAPS.get(key)

    if not mindmap:
        # Generate generic template
        mindmap = f"""mindmap
  root(({chapter_name}))
    Concept
    Key Points
    Formulas
    Applications"""

    if output_path:
        mmd_path = output_path.replace(".png", ".mmd")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(mindmap)
        return mindmap, mmd_path

    return mindmap, None

def render_mindmap(mmd_text, output_path):
    """Render Mermaid mindmap to PNG using mermaid-cli."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd",
                                      delete=False, encoding="utf-8") as f:
        f.write(mmd_text)
        mmd_path = f.name

    # Find system Chrome for Puppeteer (mermaid-cli requires it)
    chrome_paths = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    ]
    import glob as _glob
    for _p in chrome_paths:
        if __import__('os').path.exists(_p):
            __import__('os').environ.setdefault("PUPPETEER_EXECUTABLE_PATH", _p)
            break

    try:
        subprocess.run(
            ["mmdc", "-i", mmd_path, "-o", output_path,
             "-b", "transparent", "-s", "2"],
            check=True, capture_output=True, text=True, timeout=60
        )
        print(f"  Rendered: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"  [WARN] mermaid-cli failed: {e.stderr}")
        print(f"  Mindmap saved as .mmd: {mmd_path}")
        return False
    finally:
        os.unlink(mmd_path)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_mindmap.py <chapter_name> [output.png]")
        print("Available chapters:", ", ".join(CHAPTER_MAPS.keys()))
        sys.exit(1)

    chapter = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else f"{chapter}_mindmap.png"

    mindmap, _ = generate_mermaid_file(chapter, output)
    print(mindmap)
    print(f"\n--- Mermaid source above ---")

    if output.endswith(".png"):
        render_mindmap(mindmap, output)
