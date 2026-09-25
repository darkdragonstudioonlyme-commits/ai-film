# VoxCPM2 multilingual voice evaluation

This packet evaluates synthetic Voice Design, not voice cloning. No reference audio is supplied.

Pinned identity:
- OpenBMB/VoxCPM2 revision 32279effe8c19989596f05d353d1447f51d9e915
- voxcpm 2.0.3
- Apache-2.0
- native 48 kHz output
- EN, ZH and VI included in the fixed packet

The same character description and seed are reused across all three languages so cross-language identity can be compared. An and Linh use distinct descriptions/seeds. The public packet uses opaque voice-group IDs; the private map reveals character identity only after blind scoring.

Initial human acceptance is provisional: intelligibility, character match, prosody, artifact-free and overall >=4/5; every rendered line must fit its edit cue. Cross-language speaker-embedding thresholds are calibrated only after the first real VoxCPM2 outputs exist.
