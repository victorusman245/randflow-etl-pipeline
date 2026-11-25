from sqlalchemy import create_engine, text, inspect
from config import DB_URL

def load(df, table: str, schema: str = 'staging'):
    engine = create_engine(DB_URL)
    source_file = df['source_file'].iloc[0]
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema}'))
        if inspect(conn).has_table(table, schema=schema):
            conn.execute(
                text(f'DELETE FROM {schema}.{table} WHERE source_file = :f'),
                {'f': source_file},
            )
    df.to_sql(table, engine, schema=schema, if_exists='append',
              index=False, method='multi', chunksize=1000)
    return len(df)