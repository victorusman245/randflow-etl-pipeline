import pandas as pd

def _base_clean(df):
    df.columns = (
        df.columns.str.strip().str.lower()
        .str.replace(r'[^a-z0-9]+', '_', regex=True).str.strip('_')
    )
    df = df.dropna(how='all').drop_duplicates()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
    return df

def _clean_customers(df):
    df['full_name'] = df['full_name'].str.title()
    df['email_address'] = df['email_address'].str.lower().replace('', pd.NA)
    df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
    return df

def _clean_accounts(df):
    df['account_status'] = df['account_status'].str.title()
    df['opening_balance'] = pd.to_numeric(df['opening_balance'], errors='coerce')
    df['open_date'] = pd.to_datetime(df['open_date'], errors='coerce')
    return df

def _clean_transactions(df):
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['description'] = df['description'].str.title()
    df['channel'] = df['channel'].str.title()
    mask = df['transaction_type'].isin(['Deposit', 'Refund']) & (df['amount'] < 0)
    df.loc[mask, 'amount'] = df.loc[mask, 'amount'].abs()
    df = df.dropna(subset=['transaction_date', 'amount'])
    out_types = ['Purchase', 'Withdrawal', 'Transfer', 'Fee']
    df['signed_amount'] = df['amount'].where(~df['transaction_type'].isin(out_types), -df['amount'])
    return df

CLEANERS = {
    'customers': _clean_customers,
    'accounts': _clean_accounts,
    'transactions': _clean_transactions,
}

def transform(df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    df = _base_clean(df)
    table = source_file.rsplit('.', 1)[0].lower()
    if table in CLEANERS:
        df = CLEANERS[table](df)
    df['source_file'] = source_file
    df['loaded_at'] = pd.Timestamp.now(tz='UTC')
    return df