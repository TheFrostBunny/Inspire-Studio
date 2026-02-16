# Inspire Studio

Inspire Studio er en moderne, brukervennlig app for Windows som lar deg:

- **Slå sammen video og lyd**: Velg en videofil og en lydfil, og eksporter en ny video med ønsket lyd.
- **Last ned fra YouTube**: Lim inn en YouTube-lenke eller spilleliste, og last ned videoer med automatisk thumbnail.

Appen har et moderne grensesnitt bygget med Python, customtkinter og ffmpeg.

## Funksjoner
- Velg og slå sammen video (MP4, MOV, AVI, MKV) og lyd (MP3, WAV, AAC, OGG)
- Legg til egendefinert thumbnail på eksportert video
- Last ned enkeltvideoer eller hele spillelister fra YouTube
- Automatisk innbygging av cover-bilde (thumbnail) på alle nedlastede videoer
- Moderne, fargetema-basert UI

## Krav
- Python 3.8 eller nyere
- ffmpeg (må være installert og i PATH)
- customtkinter (`pip install customtkinter`)
- yt-dlp (`pip install yt-dlp`)

## Slik bruker du Inspire Studio
1. Kjør appen: `python main.py`
2. Velg "Video + Audio" for å slå sammen video og lyd, eller "YouTube" for å laste ned videoer
3. Følg instruksjonene i appen
4. Ferdig!

---
Dette er et hobbyprosjekt. For produksjon, legg til mer feilhåndtering og støtte for flere formater etter behov.
