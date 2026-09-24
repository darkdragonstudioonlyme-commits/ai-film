# Slice01 timing and animatic

timing.json is the canonical 75-second edit timing for the eight benchmark shots.

Generate committed subtitle timing assets:

  PYTHONPATH=. python3 tools/build_subtitles.py

Validate the animatic plan without ffmpeg:

  PYTHONPATH=. python3 tools/build_animatic.py --plan-only --out-root /tmp/slice01-animatic

Render placeholder 9:16 and 16:9 animatics when ffmpeg is available:

  PYTHONPATH=. python3 tools/build_animatic.py --ffmpeg /path/to/ffmpeg --aspect both --out-root /path/out

The placeholder video uses color slates plus a silent stereo audio track. EN/ZH/VI subtitles remain external so timing can be reviewed without font/render differences. Final media is not committed.
