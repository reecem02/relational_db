import pandas as pd
from sqlalchemy import create_engine, inspect
import os
import yaml
from modules.utils import load_schema
import re

schema = load_schema()

# Load DB path
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

DB_PATH = os.path.expanduser(config["database"]["path"])
engine = create_engine(f"sqlite:///{DB_PATH}")

def highlight_matches(seq, keyword, context=40, max_snippets=2):
    """Return up to max_snippets matches of keyword in seq, with up to `context` chars before/after each match."""
    import re
    matches = [m for m in re.finditer(re.escape(keyword), seq, re.IGNORECASE)]
    if not matches:
        return None
    snippets = []
    for m in matches[:max_snippets]:
        start = max(m.start() - context, 0)
        end = min(m.end() + context, len(seq))
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(seq) else ""
        snippet = f"{prefix}{seq[start:m.start()]}[{seq[m.start():m.end()]}]{seq[m.end():end]}{suffix}"
        snippets.append(snippet)
    if len(matches) > max_snippets:
        snippets.append("...more matches...")
    return " | ".join(snippets)

def search_db(keyword):
    """
    Search all tables for a keyword. If the keyword matches a Uehling Lab ID (ULXXX),
    return all metadata for that Lab ID and the first 10 FASTA sequences (first 2 lines of each).
    """
    try:
        is_lab_id = keyword.upper().startswith("UL") and keyword[2:].isdigit()

        if is_lab_id:
            # Fetch all metadata for this lab_id
            query_metadata = """
                SELECT key, value
                FROM Metadata
                WHERE lab_id = :lab_id
            """
            metadata = pd.read_sql(query_metadata, con=engine, params={"lab_id": keyword})
            metadata['type'] = 'metadata'

            # Fetch first 10 FASTA sequences for this lab_id
            query_genomic = """
                SELECT key, value
                FROM GenomicData
                WHERE lab_id = :lab_id
                LIMIT 10
            """
            fasta = pd.read_sql(query_genomic, con=engine, params={"lab_id": keyword})
            fasta['type'] = 'fasta'

            print(f"\nMetadata for {keyword}:")
            if not metadata.empty:
                print(metadata[['key', 'value']].to_string(index=False))
            else:
                print("No metadata found.")

            print(f"\nFASTA sequences for {keyword} (first 2 lines of each):")
            if not fasta.empty:
                for idx, row in fasta.iterrows():
                    seq = row['value']
                    lines = [seq[i:i+60] for i in range(0, len(seq), 60)]
                    display_lines = lines[:2]
                    print(f">{row['key']}")
                    for l in display_lines:
                        print(l)
                    if len(lines) > 2:
                        print("...")
            else:
                print("No FASTA sequences found.")

            # ---- RETURN FOR EXPORT ----
            results = pd.concat([metadata, fasta], ignore_index=True, sort=False)
            return results
        else: 
            print(f"Searching for keyword: {keyword}")
            # Otherwise, search all tables for the keyword
            results = []

            # Search Metadata
            query_metadata = """
                SELECT 'Metadata' as source, lab_id, key, value
                FROM Metadata
                WHERE lab_id LIKE :kw OR key LIKE :kw OR value LIKE :kw
            """
            results.append(pd.read_sql(query_metadata, con=engine, params={"kw": f"%{keyword}%"}))

            # Search GenomicData
            cols = ', '.join(schema["genomic_columns"])
            query_genomic = f"""
                SELECT {cols}
                FROM GenomicData
                WHERE lab_id LIKE :kw OR key LIKE :kw OR value LIKE :kw
                ORDER BY seq_order
                LIMIT 5
            """
            results.append(pd.read_sql(query_genomic, con=engine, params={"kw": f"%{keyword}%"}))

            # Combine and display results
            all_results = pd.concat(results, ignore_index=True)
            all_results = all_results.dropna(how='all', subset=[col for col in all_results.columns if col != 'source']) # Drops rows where all colmns except 'source' are empty
            
            # Remove 'source' and 'seq_order' columns for display
            display_cols = [col for col in all_results.columns if col not in ('source', 'seq_order')]
            display_df = all_results[display_cols]

            display_df = display_df.dropna(how='all')

            if 'value' in display_df.columns:
                def smart_truncate(row):
                    val = str(row['value'])
                    if pd.isna(val):
                        return val
                    # Only highlight if the search term is in the value (for genomic data)
                    if keyword.lower() in val.lower():
                        return highlight_matches(val, keyword, context=40, max_snippets=2)
                    else:
                        # fallback: show first 40 chars as before
                        return val[:40] + '...' if len(val) > 40 else val

                display_df.loc[:, 'value'] = display_df.apply(smart_truncate, axis=1)
                display_df = display_df.dropna(subset=['key', 'value'], how='all')

            if not display_df.empty:
                print(f"Results for keyword '{keyword}':")
                print(display_df.head(10).to_string(index=False))
            else:
                print(f"No results found for: {keyword}")
            return display_df

    except Exception as e:
        print(f"Error querying data: {e}")

    