import pandas as pd
import requests
import os
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.models.srag import SragRecord
from io import StringIO
import logging

logging.basicConfig(level=logging.INFO)

# URL do arquivo CSV
DATA_URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2019/INFLUD19-26-06-2025.csv"

COLUMNS_TO_KEEP = {
    'DT_NOTIFIC': 'dt_notific',
    'SG_UF_NOT': 'sg_uf',
    'CS_SEXO': 'cs_sexo',
    'NU_IDADE_N': 'nu_idade_n',
    'UTI': 'uti',
    'EVOLUCAO': 'evolucao',
    'VACINA_COV': 'vacina_cov'
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e transforma os dados do DataFrame."""

    df['dt_notific'] = pd.to_datetime(
        df['dt_notific'], format='%Y-%m-%d', errors='coerce')

    df['uti'] = df['uti'].apply(lambda x: True if x == 1.0 else False)
    df['vacina_cov'] = df['vacina_cov'].apply(
        lambda x: True if x == 1.0 else False)

    df['evolucao'] = pd.to_numeric(
        df['evolucao'], errors='coerce').astype('Int64')

    df.dropna(subset=['dt_notific'], inplace=True)
    return df


def import_data():
    logging.info(f"Baixando dados de {DATA_URL}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(DATA_URL, headers=headers)
        response.raise_for_status()
        csv_data = StringIO(response.text)
    except requests.RequestException as e:
        logging.error(f"Erro ao baixar os dados: {e}")
        return

    Session = sessionmaker(bind=engine)
    db_session = Session()

    chunk_size = 50000
    total_rows = 0

    try:
        logging.info("Iniciando a importação para o banco de dados...")
        for chunk in pd.read_csv(csv_data, sep=';', usecols=COLUMNS_TO_KEEP.keys(), chunksize=chunk_size, low_memory=False):
            chunk.rename(columns=COLUMNS_TO_KEEP, inplace=True)
            cleaned_chunk = clean_data(chunk)

            records = cleaned_chunk.to_dict(orient='records')

            db_session.bulk_insert_mappings(SragRecord, records)
            db_session.commit()

            total_rows += len(cleaned_chunk)
            logging.info(f"{total_rows} registros importados...")

        logging.info("Importação concluída com sucesso!")
    except Exception as e:
        db_session.rollback()
        logging.error(f"Ocorreu um erro durante a importação: {e}")
    finally:
        db_session.close()


if __name__ == "__main__":

    from app.db.base import Base
    logging.info("Criando tabelas se não existirem...")
    Base.metadata.create_all(bind=engine)

    import_data()
