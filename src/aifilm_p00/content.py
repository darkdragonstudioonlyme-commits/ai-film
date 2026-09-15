"""Reproducible source/test content identity without output/self-hash cycles."""
from pathlib import Path
from .codec import sha256,digest
from .errors import require
SOURCE_DIRS=('src','schemas','config','native')
TEST_DIRS=('tests','fixtures','tools')


def inventory(root,directories):
    root=Path(root);rows=[]
    for directory in directories:
        for path in sorted((root/directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':
                require(not path.is_symlink(),15,'BUILD_MEMBER_SYMLINK')
                data=path.read_bytes();rows.append({'path':path.relative_to(root).as_posix(),
                                                   'bytes':len(data),'sha256':sha256(data)})
    require(bool(rows),15,'BUILD_INVENTORY_EMPTY')
    return rows


def content_identity(root):
    source=inventory(root,SOURCE_DIRS);tests=inventory(root,TEST_DIRS)
    return {'source_content_digest':digest(source),'test_content_digest':digest(tests),
            'source_members':source,'test_members':tests}
