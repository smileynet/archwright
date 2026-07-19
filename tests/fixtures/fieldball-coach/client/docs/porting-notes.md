# Porting Notes

Desktop builds previously shelled out via OS.execute("ffmpeg", args) to encode
replay clips. That path is gone — replays render in-engine now. Keeping the note
for anyone wondering where the encoder went.

If include-glob filtering in the check tool ever regresses, the no-shell-exec
conformance check will match this prose line and fail the suite — that is by design.
