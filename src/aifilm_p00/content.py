"""Reviewed-file identity for the exact V2 contract set."""
from pathlib import Path
from .codec import sha256,read_bytes
from .errors import require

APPROVED={
'PHASE00_INFRA_DESIGN_V2.md':'6c24fe2776afc6a9cc323e2b29ca8ef29a2276973471360e156435e07e04f577',
'PHASE00_ACCEPTANCE_MATRIX_V2.md':'700f6f19c952da8b64aa5fbcbf32f0e33784170496108984441130092f60699f',
'PHASE00_FAILURE_RECOVERY_PLAN_V2.md':'db4109b84b8c13c021464e9587d8612ab2210e6ade274a052549311d46c99a35',
'PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2.md':'3b577c7a57da29e661c2c157ec74233c6aa60ea174830d1e67e1cfc373457890'}

def approved_set(root:Path):
    records=[]
    for name,want in APPROVED.items():
        path=root/'contracts'/name
        actual=sha256(read_bytes(path,1024*1024))
        require(actual==want,16,'APPROVED_CONTRACT_CHANGED')
        records.append({'name':name,'sha256':actual})
    return records
