# ChessTournamentAnalysis
## moves.csv
- round PK
- move number (Int32)
- move
- color
- evaluation (double)
- time
- time (seconds) (Int32)

## details.csv
- round PK
- event
- white FK FideId
- black FK FideId
- ECO FK

## players.csv
- name
- FideId PK
- Elo (Int32)

## openings.csv
- ECO PK
- name
