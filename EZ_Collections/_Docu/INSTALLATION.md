# Guida Installazione EZCollections V5

## 📦 Metodo 1: Installazione Diretta (Raccomandato)

1. **Copia la cartella `ez_collections`** nella directory degli addon di Blender:
   - **Windows**: `C:\Users\[TuoNome]\AppData\Roaming\Blender Foundation\Blender\[Versione]\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/[Versione]/scripts/addons/`
   - **Linux**: `~/.config/blender/[Versione]/scripts/addons/`

2. **Apri Blender** → Edit → Preferences → Add-ons

3. **Cerca "EZCollections V5"** nella lista

4. **Attiva l'addon** spuntando la checkbox

5. **Premi Ctrl+G** per verificare che il Pie Menu funzioni!

## 📦 Metodo 2: Installazione da ZIP

1. **Comprimi la cartella `ez_collections`** in un file ZIP
   - Il file ZIP deve contenere direttamente la cartella `ez_collections`

2. **Apri Blender** → Edit → Preferences → Add-ons

3. **Clicca "Install..."** in alto a destra

4. **Seleziona il file ZIP** e clicca "Install Add-on"

5. **Cerca "EZCollections V5"** e attivalo

6. **Premi Ctrl+G** per testare!

## ✅ Verifica Installazione

Dopo l'installazione dovresti vedere:

- **Pie Menu**: Premi `Ctrl+G` in Object Mode → Apparirà il menu circolare
- **N-Panel**: Premi `N` in 3D View → Cerca tab "EZ Collections"
- **Preferences**: Edit → Preferences → Add-ons → EZCollections V5

## 🔧 Troubleshooting

### L'addon non appare nella lista
- Verifica che la cartella sia `ez_collections` (tutto minuscolo)
- Controlla che dentro ci sia il file `__init__.py`
- Riavvia Blender

### Errori di importazione
- Verifica di avere Blender 4.5 o superiore
- Controlla che tutti i file `.py` siano presenti
- Controlla la Console di Blender (Window → Toggle System Console)

### Il Pie Menu non funziona
- Verifica che l'addon sia attivato
- Controlla che nessun altro addon usi Ctrl+G
- Prova a salvare le preferenze e riavviare

## 🆚 Migrazione da EZCollections V4

Se stavi usando la versione V4 (monoscript):

1. **Disattiva** il vecchio "EZCollections 3.0" dalle preferenze
2. **Installa** EZCollections V5 seguendo i metodi sopra
3. **Nota**: Le funzionalità Pivot e Shared Modifier sono state rimosse

## 🎯 Primo Utilizzo

1. Seleziona alcuni oggetti nella scena
2. Premi `Ctrl+G`
3. Clicca su "Create"
4. Inserisci un nome per la collection
5. La collection sarà creata automaticamente!

## 📚 Documentazione Completa

Consulta il file `README.md` per la documentazione completa delle funzionalità.
