"""Bounded append admission; never rotate/delete/truncate an unresolved journal."""
from dataclasses import dataclass
from .errors import require

RECOVERY_HEADROOM = 512 * 1024


@dataclass
class JournalBudget:
    ceiling: int
    initial_bytes: int
    allowed_bytes: int
    recovery: bool = False
    spent: int = 0

    @classmethod
    def reserve(cls, ceiling, current, additional, *, recovery=False):
        require(all(type(v) is int and v >= 0 for v in (ceiling,current,additional))
                and additional >= 4096, 10, 'JOURNAL_RESERVATION_SCHEMA')
        headroom = 0 if recovery else RECOVERY_HEADROOM
        require(current + additional + headroom <= ceiling, 13, 'JOURNAL_CAPACITY')
        return cls(ceiling, current, additional, recovery)

    def check(self, current, length):
        require(type(length) is int and length > 0, 10, 'JOURNAL_APPEND_LENGTH')
        require(current == self.initial_bytes + self.spent, 16, 'JOURNAL_EXTERNAL_WRITE')
        require(self.spent + length <= self.allowed_bytes, 13, 'JOURNAL_RESERVATION_EXHAUSTED')
        require(current + length <= self.ceiling - (0 if self.recovery else RECOVERY_HEADROOM),
                13, 'JOURNAL_CAPACITY')

    def committed(self, old_size, new_size, length):
        self.check(old_size, length)
        require(new_size == old_size + length, 15, 'JOURNAL_WRITE_SIZE')
        self.spent += length
