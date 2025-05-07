import pandas as pd

def calculate_federal(income):
    df = pd.read_csv('data/fed_2025.csv')
    df['low_range'] = pd.to_numeric(df['low_range'], errors='coerce')
    df['high_range'] = pd.to_numeric(df['high_range'], errors='coerce')
    df['tax_rate'] = pd.to_numeric(df['tax_rate'], errors='coerce')

    tax = 0.0
    for _, row in df.iterrows():
        low = row['low_range']
        high = row['high_range']
        rate = row['tax_rate']

        if income > low:
            taxable_income = min(income, high) - low
            tax += taxable_income * rate

    return tax

def calculate_provincial(income, province):
    df = pd.read_csv('data/prov_2025.csv')
    df = df[df['prov'] == province.upper()].reset_index(drop=True)

    df['low_range'] = pd.to_numeric(df['low_range'], errors='coerce')
    df['high_range'] = pd.to_numeric(df['high_range'], errors='coerce')
    df['tax_rate'] = pd.to_numeric(df['tax_rate'], errors='coerce')

    tax = 0.0
    for _, row in df.iterrows():
        low = row['low_range']
        high = row['high_range']
        rate = row['tax_rate']

        if income > low:
            taxable_income = min(income, high) - low
            tax += taxable_income * rate

    return tax


def calculate_tax(income, province):
    """
    Calculate total tax based on income and province.
    """
    return calculate_federal(income) + calculate_provincial(income, province)

def calculate_net_income(income, province):
    """
    Calculate net income after tax.
    """
    return income - calculate_tax(income, province)

def calculate_tax_bracket(income, province):
    df = pd.read_csv('data/prov_2025.csv')
    df.columns = df.columns.str.strip()
    df = df[df['prov'].str.upper() == province].reset_index(drop=True)
    df['low_range'] = pd.to_numeric(df['low_range'], errors='coerce')
    df['high_range'] = pd.to_numeric(df['high_range'], errors='coerce')
    df['tax_rate'] = pd.to_numeric(df['tax_rate'], errors='coerce')

    for _, row in df.iterrows():
        if income >= row['low_range'] and income <= row['high_range']:
            return row['tax_rate']
    return 0

def income_from_total_tax(paid, province, step=0.01):
    """
    Calculate the income required to pay a specific amount of tax."""
    pf = pd.read_csv('data/fed_2025.csv')
    pp = pd.read_csv('data/prov_2025.csv')
    pp = pp[pp['prov'] == province.upper()]
    pf[['low_range', 'high_range', 'tax_rate']] = pf[['low_range', 'high_range', 'tax_rate']].apply(pd.to_numeric)
    pp[['low_range', 'high_range', 'tax_rate']] = pp[['low_range', 'high_range', 'tax_rate']].apply(pd.to_numeric)

    def tax_for(x):
        return calculate_federal(x) + calculate_provincial(x, province)

    tax = 0
    inc = 0
    while tax < paid:                       # linear crawl; fast enough in 0.01 steps
        inc += step
        tax = tax_for(inc)
        if inc > 1e8:                       # safety bail‑out
            break
    return inc

def main():
    """
    Main function to run the calculator.
    """
    income = float(input("Enter your income: "))
    province = input("Enter your province (e.g., ON, BC): ").upper()
    
    total_tax = calculate_tax(income, province)
    net_income = calculate_net_income(income, province)
    tax_bracket = calculate_tax_bracket(income, province)
    
    print(f"Total Tax: ${total_tax:.2f}")
    print(f"Net Income: ${net_income:.2f}")
    print(f"Provincial Tax Bracket: {tax_bracket * 100:.2f}%")
    
# This script calculates the federal and provincial tax based on the user's income and province.
if __name__ == "__main__":
    main()
