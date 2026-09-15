"""Native executable-script bytes pinned to the exact reviewed build inventory.

Do not hash whatever bytes happen to be present and then call that hash trusted.
The complete inventory must first match the build bound by current authority.
"""
from contextlib import contextmanager
from pathlib import Path

from ..codec import digest, relative, sha256
from ..errors import require

class SourcePins:
    def __init__(self, root, paths, identity, build_digest):
        require(identity.get('source_content_digest')==build_digest
                and digest(identity.get('source_members'))==build_digest,16,'SOURCE_INVENTORY_IDENTITY')
        rows=identity['source_members']
        require(type(rows) is list and len({r['path'] for r in rows})==len(rows),15,'SOURCE_INVENTORY_DUPLICATE')
        self.rows={row['path']:dict(row) for row in rows}
        self.root=Path(root);self.paths=paths;self.build_digest=build_digest

    def member(self,name):
        relative(name)
        require(name in self.rows,15,'SOURCE_MEMBER_NOT_REVIEWED')
        return self.rows[name]

    def read(self,name):
        row=self.member(name);path=str(self.root/name)
        require(row['bytes']<=10*1024**2,22,'SOURCE_MEMBER_CAP')
        with self.paths.pin(path,confidential=False) as pinned:
            require(pinned.identity['bytes']==row['bytes'],15,'SOURCE_MEMBER_SIZE')
            raw=self.paths.api.read(pinned.handle,row['bytes']+1)
            require(len(raw)==row['bytes'] and sha256(raw)==row['sha256'],15,'SOURCE_MEMBER_HASH')
            return raw

    @contextmanager
    def path(self,name):
        """Path-executed PowerShell keeps exact leaf/ancestors held through run."""
        row=self.member(name);path=str(self.root/name)
        with self.paths.pinned_payload(path,row['sha256'],row['bytes']):
            yield path
