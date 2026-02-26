# EZCollections V5 - Modern Collection Manager

**Addon moderno per Blender 4.5+ per gestione avanzata delle collection**

## 🎯 Caratteristiche Principali

- **Struttura Modulare**: Codice organizzato in moduli separati per facilità di manutenzione
- **Naming Personalizzabile**: Prefix/suffix automatici per collection
- **Workflow Maya-Style**: Gestione rapida tramite Pie Menu (Ctrl+G)
- **N-Panel Integrato**: Controlli completi nella sidebar
- **Modalità Solo**: Isola rapidamente collection per lavorare focalizzati

## 📦 Installazione

1. Copia la cartella `ez_collections` in Blender addons directory
2. Apri Blender → Edit → Preferences → Add-ons
3. Cerca "EZCollections V5"
4. Attiva l'addon

## 🚀 Utilizzo

### Pie Menu (Ctrl+G)
- **Add**: Aggiungi oggetti alla collection attiva
- **Remove**: Rimuovi oggetti dalla collection
- **Create**: Crea nuova collection con naming personalizzato
- **Solo**: Isola/mostra collection

### N-Panel (View3D > EZ Collections)
- Configura prefix/suffix per naming
- Preview in tempo reale dei nomi
- Scegli colore default collections
- Modalità creazione (root/active)
- Quick Actions per operazioni rapide

### Preferences (Edit → Preferences → Add-ons → EZCollections V5)
- Collection Prefix: Prefisso automatico
- Collection Suffix: Suffisso automatico
- Collection Color: Colore predefinito
- Creation Mode: Root o Active collection

## 🏗️ Struttura del Codice

```
ez_collections/
├── __init__.py              # Registrazione principale addon
├── preferences.py           # Preferenze addon
├── core/
│   ├── __init__.py
│   ├── collection.py        # EZCollection class
│   └── utils.py             # Funzioni utility
├── operators/
│   ├── __init__.py
│   ├── create_collection.py # Creazione collection
│   ├── add_remove.py        # Add/Remove operatori
│   └── visibility.py        # Solo mode
└── ui/
    ├── __init__.py
    ├── pie_menu.py          # Pie menu (Ctrl+G)
    └── panel.py             # N-Panel sidebar
```

## 🔧 Funzionalità Rimosse (da V4)

- ❌ Sistema Pivot Collection (rimosso)
- ❌ Shared Modifier System (rimosso)
- ❌ Handler automatico selezione pivot (rimosso)
- ❌ Lock/Unlock pivot operators (rimosso)

## ✨ Nuove Funzionalità (V5)

- ✅ Sistema naming prefix/suffix
- ✅ Preview in tempo reale
- ✅ Modalità creazione flessibile
- ✅ N-Panel moderno
- ✅ Architettura modulare
- ✅ Codice pulito e manutenibile

## 📝 Note di Sviluppo

- Compatibile con Blender 4.5+
- Python 3.11+
- Struttura modulare per facile estensione
- Sistema singleton per EZCollection instances
- Cleanup automatico istanze non valide

## 👥 Autori

**Lex & Manu**

## 📄 Licenza

Uso personale e didattico
