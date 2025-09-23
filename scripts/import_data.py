import pandas as pd
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.db.session import engine
from app.models.srag import SragRecord
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de todas as fontes de dados
DATA_URLS = [
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2019/INFLUD19-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2020/INFLUD20-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2021/INFLUD21-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2022/INFLUD22-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2023/INFLUD23-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-26-06-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-22-09-2025.csv"
]

COLUMNS_TO_KEEP = {
    'DT_NOTIFIC': 'dt_notific', 'SG_UF_NOT': 'sg_uf', 'CS_SEXO': 'cs_sexo',
    'NU_IDADE_N': 'nu_idade_n', 'UTI': 'uti', 'EVOLUCAO': 'evolucao',
    'VACINA_COV': 'vacina_cov'
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e transforma os dados do DataFrame."""

    dt_series = pd.to_datetime(
        df['dt_notific'], format='%d/%m/%Y', errors='coerce', dayfirst=True)

    dt_series_fallback = pd.to_datetime(
        df['dt_notific'], format='%Y-%m-%d', errors='coerce')

    df['dt_notific'] = dt_series.fillna(dt_series_fallback)

    df.dropna(subset=['dt_notific'], inplace=True)
    df['uti'] = df['uti'].apply(lambda x: True if x == 1.0 else False)
    df['vacina_cov'] = df['vacina_cov'].apply(
        lambda x: True if x == 1.0 else False)
    df['evolucao'] = pd.to_numeric(
        df['evolucao'], errors='coerce').astype('Int64')
    return df


def clear_table(db_session):
    """Apaga todos os registros da tabela srag_records."""
    logging.info(
        "Limpando a tabela 'srag_records' antes da nova importação...")
    db_session.execute(
        text(f"TRUNCATE TABLE {SragRecord.__tablename__} RESTART IDENTITY;"))
    db_session.commit()
    logging.info("Tabela limpa com sucesso.")


def import_data():
    """Baixa, limpa e insere os dados de todas as URLs usando streaming."""
    Session = sessionmaker(bind=engine)
    db_session = Session()
    clear_table(db_session)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    grand_total_rows = 0

    for url in DATA_URLS:
        logging.info(f"--- Processando URL: {url} ---")
        try:
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()

                chunk_size = 50000
                total_rows_for_file = 0

                logging.info(
                    f"Iniciando a importação via streaming para o banco de dados...")
                for chunk in pd.read_csv(response.raw, sep=';', usecols=COLUMNS_TO_KEEP.keys(), chunksize=chunk_size, low_memory=False, encoding='ISO-8859-1'):
                    chunk.rename(columns=COLUMNS_TO_KEEP, inplace=True)
                    cleaned_chunk = clean_data(chunk)

                    records = cleaned_chunk.to_dict(orient='records')
                    if not records:
                        continue

                    db_session.bulk_insert_mappings(SragRecord, records)
                    db_session.commit()

                    total_rows_for_file += len(cleaned_chunk)
                    logging.info(
                        f"{total_rows_for_file} registros importados deste arquivo...")

                grand_total_rows += total_rows_for_file
                logging.info(
                    f"Importação do arquivo concluída! Total até agora: {grand_total_rows} registros.")

        except requests.RequestException as e:
            logging.error(
                f"Erro ao baixar os dados de {url}: {e}. Pulando para o próximo.")
            continue
        except Exception as e:
            db_session.rollback()
            logging.error(
                f"Ocorreu um erro durante a importação do arquivo {url}: {e}")

    db_session.close()
    logging.info(f"--- IMPORTAÇÃO FINALIZADA ---")
    logging.info(f"Total geral de registros importados: {grand_total_rows}")


if __name__ == "__main__":
    from app.db.base import Base
    logging.info("Garantindo que as tabelas existam...")
    Base.metadata.create_all(bind=engine)

    import_data()
