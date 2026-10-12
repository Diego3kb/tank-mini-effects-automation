import hashlib
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from atkm import RECORD_SIZE, SLOTS, TRAILER


def make_bundle(path: Path) -> str:
    """Banco ATKM sintético valido: 21 registros de 92 bytes + rodape."""
    record = bytearray(RECORD_SIZE)
    record[0] = 100          # volume
    record[3:8] = b"\x01\x02\x03\x04\x05"  # ordem da cadeia
    record[8:14] = b"\x01" * 6             # modulos ligados
    for offset in (20, 22, 24, 26, 32, 34, 36, 38, 40, 44, 46, 48, 50, 52,
                   54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80):
        record[offset:offset + 2] = (50).to_bytes(2, "little")
    data = bytes(record) * len(SLOTS) + TRAILER
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()
